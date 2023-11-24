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
