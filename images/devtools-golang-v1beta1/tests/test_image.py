import logging
import os
import pytest
import shutil
import subprocess
import sys

from contextlib import contextmanager
from pathlib import Path, PurePath
from pytest import CaptureFixture
from typing import Dict, Iterator, List, Optional, TypeVar, Union

TEST_DIR = Path(__file__).parent.absolute()
PROTOTYPE_DIR = TEST_DIR / "prototype"

PathLike = Union[PurePath, str]
PathLikeT = TypeVar("PathLikeT", bound=PathLike)


@contextmanager
def ctx_prototype(tmp_path: Path) -> Iterator[Path]:
    workdir = tmp_path / "base"
    logging.info("workdir = %s", workdir)
    shutil.copytree(PROTOTYPE_DIR, workdir)

    with ctx_chdir(workdir):
        yield workdir


@contextmanager
def ctx_chdir(newdir: PathLikeT) -> Iterator[PathLikeT]:
    cwd = os.getcwd()
    try:
        os.chdir(f"{newdir}")
        yield newdir
    finally:
        os.chdir(cwd)


def test_prototype_ok() -> None:
    with ctx_chdir(PROTOTYPE_DIR):
        subprocess.run("docker-compose run --rm devtools".split(" "), check=True)
        assert (PROTOTYPE_DIR / "coverage.out").exists()


@pytest.mark.parametrize(
    ["command", "success", "files", "expected_outputs"],
    [
        (
            None,
            False,
            {
                "bad_file.go": """\
package main

func NoDocs() int {
	return 3
}

func init() {
	print(NoDocs())
}
"""
            },
            ["exported function NoDocs should have comment or be unexported"],
        ),
        (
            None,
            False,
            {
                "bad_file.go": """\
package main

import "fmt"

// GetError is a function
func GetError() (int, error) {
	return 3, fmt.Errorf("foo")
}

func init() {
	x, _ := GetError()
	print(x)
}
""",
            },
            ["Error return value is not checked"],
        ),
        (
            None,
            False,
            {
                "bad_file.go": """\
package main

func UnusedFunc() int {
	return 3
}
"""
            },
            ["`UnusedFunc` is unused"],
        ),
        (
            None,
            True,
            {
                ".golangci.yml": """\
linters:
  disable-all: true
  enable: [ misspell ]
"""
            },
            [""],
        ),
    ],
)
def test_alterations(
    tmp_path: Path,
    capfd: CaptureFixture[str],
    command: Optional[List[str]],
    success: bool,
    files: Optional[Dict[str, str]],
    expected_outputs: List[str],
) -> None:
    if command is None:
        command = "docker-compose run --rm devtools".split(" ")
    if files is None:
        files = {}
    with ctx_prototype(tmp_path) as workdir:
        for file_name, file_content in files.items():
            (workdir / file_name).write_text(file_content)
        if success:
            subprocess.run(command, check=True)
        else:
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.run(command, check=True)
        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)

        for expected_output in expected_outputs:
            assert expected_output in (captured.out + captured.err)


def test_prototype_failing_tests(tmp_path: Path, capfd: CaptureFixture[str]) -> None:
    with ctx_prototype(tmp_path) as workdir:
        (workdir / "sum/failing_test.go").write_text(
            """\
package sum_test

import "testing"

func TestThatFails(t *testing.T) {
	t.Fatalf("fail")
}
"""
        )
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run("docker-compose run --rm devtools".split(" "), check=True)
        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)

        assert "FAIL: TestThatFails" in captured.out


def test_prototype_validate_fix(tmp_path: Path) -> None:
    with ctx_prototype(tmp_path) as workdir:
        (workdir / "bad_file.go").write_text(
            """\
package main

import "fmt"
import "strings"

type s struct {
	field string
	anotherField string
}

func init() {
	x := &s{
		field: fmt.Sprintf("Hell%v", 0),
		anotherField:strings.Join([]string{"wor", "ld"}, ""),
	}
	print(x)
}
"""
        )
        subprocess.run(
            "docker-compose run --rm devtools validate-fix".split(" "), check=True
        )

        formatted_file = """\
package main

import (
	"fmt"
	"strings"
)

type s struct {
	field        string
	anotherField string
}

func init() {
	x := &s{
		field:        fmt.Sprintf("Hell%v", 0),
		anotherField: strings.Join([]string{"wor", "ld"}, ""),
	}
	print(x)
}
"""

        assert formatted_file == open(workdir / "bad_file.go").read()
