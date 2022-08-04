import logging
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Iterator, List, TypeVar, Union

import pytest
from _pytest.capture import CaptureResult
from pytest import CaptureFixture

TEST_DIR = Path(__file__).parent.absolute()
PROTOTYPE_DIR = TEST_DIR / "prototype"

PathLike = Union[PurePath, str]
PathLikeT = TypeVar("PathLikeT", bound=PathLike)


@contextmanager
def ctx_chdir(newdir: PathLikeT) -> Iterator[PathLikeT]:
    cwd = os.getcwd()
    try:
        os.chdir(f"{newdir}")
        yield newdir
    finally:
        os.chdir(cwd)


@contextmanager
def ctx_prototype(tmp_path: Path) -> Iterator[Path]:
    workdir = tmp_path / "base"
    logging.info("workdir = %s", workdir)
    shutil.copytree(PROTOTYPE_DIR, workdir)

    with ctx_chdir(workdir):
        yield workdir


@dataclass
class Captured:
    result: CaptureResult[str]
    out: str
    out_lines: List[str]
    err: str
    err_lines: List[str]


def get_captured_lines(capfd: CaptureFixture[str]) -> Captured:
    captured = capfd.readouterr()
    out = captured.out
    err = captured.err
    with capfd.disabled():
        sys.stdout.write("captured.out:\n")
        sys.stdout.write(captured.out)
        sys.stderr.write("captured.err:\n")
        sys.stderr.write(captured.err)
    return Captured(captured, out, out.splitlines(), err, err.splitlines())


def test_prototype_ok(tmp_path: Path, capfd: CaptureFixture[str]) -> None:
    with ctx_prototype(tmp_path):
        subprocess.run("docker compose run --rm devtools".split(" "), check=True)
        cap = get_captured_lines(capfd)
        assert len(re.findall("Validation of .* completed", cap.out)) == 3
        subprocess.run(
            "docker compose run --rm devtools maker validate".split(" "), check=True
        )
        cap = get_captured_lines(capfd)
        assert len(re.findall("Validation of .* completed", cap.out)) == 3
        assert len(re.findall("Deployment helloworld is valid", cap.out)) == 3


def test_prototype_overlay_override(tmp_path: Path, capfd: CaptureFixture[str]) -> None:
    with ctx_prototype(tmp_path) as _:
        subprocess.run(
            "docker compose run --rm devtools validate OVERLAYS=kubernetes/overlay/staging".split(
                " "
            ),
            check=True,
        )
        cap = get_captured_lines(capfd)
        assert len(re.findall("Validation of .* completed", cap.out)) == 1

        subprocess.run(
            "docker compose run --rm devtools validate OVERLAYS=".split(" "), check=True
        )
        cap = get_captured_lines(capfd)
        assert sum("make: Nothing to be done" in line for line in cap.out_lines) == 1


def test_prototype_fail_validate(tmp_path: Path, capfd: CaptureFixture[str]) -> None:
    with ctx_prototype(tmp_path) as workdir:
        path = workdir / "kubernetes/base/deployment.yaml"
        cnf = path.read_text()
        cnf = re.sub(
            r"\s+ephemeral-storage:.*([\r\n])", r"\1", cnf
        )  # Delete all lines with this limit preserving newline
        path.write_text(cnf)

        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(
                "docker compose run --rm devtools validate OVERLAYS=kubernetes/base".split(
                    " "
                ),
                check=True,
            )
        cap = get_captured_lines(capfd)
        assert (
            sum("Ephemeral Storage limit is not set" in line for line in cap.out_lines)
            == 1
        )
