import logging
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path, PurePath
from typing import (
    Callable,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import pytest
from _pytest.capture import CaptureResult
from pytest import CaptureFixture

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


def test_prototype_ok(capfd: CaptureFixture[str]) -> None:
    with ctx_chdir(PROTOTYPE_DIR):
        subprocess.run("docker compose run --rm devtools".split(" "), check=True)
        assert (PROTOTYPE_DIR / "coverage.out").exists()
        (PROTOTYPE_DIR / "coverage.out").unlink()
        assert not (PROTOTYPE_DIR / "coverage.out").exists()
        subprocess.run(
            "docker compose run --rm devtools maker validate".split(" "), check=True
        )
        assert (PROTOTYPE_DIR / "coverage.out").exists()

    cap = Captured.from_capfd(capfd)
    assert "oci.tar" not in cap.all()


@dataclass
class Captured:
    result: CaptureResult[str]
    out: str
    out_lines: List[str]
    err: str
    err_lines: List[str]

    @cached_property
    def all_lines(self) -> List[str]:
        return self.out_lines + self.err_lines

    def all(self) -> str:
        return "\n".join(self.all_lines)

    @classmethod
    def from_capfd(cls, capfd: CaptureFixture[str]) -> "Captured":
        captured = capfd.readouterr()
        out = captured.out
        err = captured.err
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        return Captured(captured, out, out.splitlines(), err, err.splitlines())


@pytest.mark.parametrize(
    ["command", "success", "mutators", "matchers"],
    [
        pytest.param(
            None,
            False,
            (
                lambda workdir: (workdir / "bad_file.go").write_text(
                    """\
package main

func NoDocs() int {
	return 3
}

func init() {
	print(NoDocs())
}
"""
                )
            ),
            [("exported function NoDocs should have comment or be unexported", True)],
            id="validate-exported-comment",
        ),
        pytest.param(
            None,
            False,
            (
                lambda workdir: (workdir / "bad_file.go").write_text(
                    """\
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
"""
                )
            ),
            [("Error return value is not checked", True)],
            id="validate-unchecked-return",
        ),
        pytest.param(
            None,
            False,
            (
                lambda workdir: (workdir / "bad_file.go").write_text(
                    """\
package main

func UnusedFunc() int {
	return 3
}
"""
                )
            ),
            [("`UnusedFunc` is unused", True)],
            id="validate-unchecked-return",
        ),
        pytest.param(
            None,
            True,
            [
                (
                    lambda workdir: (workdir / ".golangci.yml").write_text(
                        """\
linters:
  disable-all: true
  enable: [ misspell ]
"""
                    )
                ),
                (
                    lambda workdir: (workdir / "bad_file.go").write_text(
                        """\
package main

func UnusedFunc() int {
	return 3
}
"""
                    )
                ),
            ],
            [],
            id="golangci-config-used",
        ),
        pytest.param(
            None,
            True,
            [
                (
                    lambda workdir: (
                        workdir / "build/package/Dockerfile.example"
                    ).rename(workdir / "build/package/Dockerfile")
                ),
            ],
            [
                ("hadolint", True),
                ("dockle", True),
                ("var/oci_images/stage-runtime.oci.tar", True),
            ],
            id="docker-builds",
        ),
    ],
)
def test_alterations(
    tmp_path: Path,
    capfd: CaptureFixture[str],
    mutators: Union[Iterable[Callable[[Path], None]], Callable[[Path], None]],
    command: Optional[List[str]],
    success: bool,
    matchers: Iterable[Tuple[str, bool]],
) -> None:
    if command is None:
        command = "docker compose run --rm devtools".split(" ")
    if not isinstance(mutators, Iterable):
        mutators = [mutators]
    with ExitStack() as xstack:
        workdir = xstack.enter_context(ctx_prototype(tmp_path))
        for mutator in mutators:
            mutator(workdir)
        if not success:
            xstack.enter_context(pytest.raises(subprocess.CalledProcessError))
        subprocess.run(command, check=True)

    cap = Captured.from_capfd(capfd)

    for match_string, match_positive in matchers:
        found = (
            next((line for line in cap.all_lines if match_string in line), None)
            is not None
        )
        if match_positive:
            assert (
                found
            ), f"did not find {match_string} in output ...{found}\n{cap.all()}"
        else:

            assert not found, f"found {match_string} in output{found}\n{cap.all()}"


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
            subprocess.run("docker compose run --rm devtools".split(" "), check=True)
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
            "docker compose run --rm devtools validate-fix".split(" "), check=True
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


@pytest.fixture(scope="module")
def prototype_ro() -> Generator[Path, None, None]:
    _tmp_path = tempfile.mkdtemp("-devtools-terraform-cache")
    tmp_path = Path(_tmp_path)
    try:
        with ctx_prototype(tmp_path) as proto_path:
            yield proto_path
    finally:
        try:
            shutil.rmtree(tmp_path, ignore_errors=True)
        except Exception:
            logging.warning("failed to rmtree %s", tmp_path, exc_info=True)


@pytest.mark.parametrize(
    "command",
    [
        "modd --version".split(),
        "mockgen -version".split(),
        "protoc-gen-go --version".split(),
        "protoc-gen-go-grpc -version".split(),
    ],
)
def test_commands_run(prototype_ro: Path, command: List[str]) -> None:
    subprocess.run("docker compose run --rm devtools".split(" ") + command, check=True)
