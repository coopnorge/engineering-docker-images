from contextlib import contextmanager
import glob
import os
from pathlib import Path, PurePath
import logging
import shutil
import subprocess
import sys
import tempfile
from typing import Iterator, Optional, TypeVar, Union, Generator

import pytest
from pytest import CaptureFixture

TEST_DIR = Path(__file__).parent.absolute()
PROTYPE_DIR = TEST_DIR / "prototype"

RAPID_TEST = len(os.environ.get("RAPID_TEST", "")) > 0
KEEP_TMP = len(os.environ.get("KEEP_TMP", "")) > 0

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
def ctx_prototype(
    tmp_path: Path, dottf_dir: Optional[Path]
) -> Generator[Path, None, None]:
    logging.debug("RAPID_TEST = %s", RAPID_TEST)
    workdir = tmp_path / "base"
    logging.info("workdir = %s, dottf_dir = %s", workdir, dottf_dir)
    shutil.copytree(
        PROTYPE_DIR,
        workdir,
        ignore=shutil.ignore_patterns(".terraform", ".terraform.lock.hcl")
        if not RAPID_TEST
        else None,
    )
    if not RAPID_TEST:
        assert dottf_dir is not None
        shutil.copytree(dottf_dir, workdir / ".terraform")
        shutil.copy2(
            dottf_dir.parent / ".terraform.lock.hcl", workdir / ".terraform.lock.hcl"
        )

    with ctx_chdir(workdir):
        yield workdir


@contextmanager
def ctx_dottf_dir() -> Generator[Optional[Path], None, None]:
    logging.debug("RAPID_TEST = %s", RAPID_TEST)
    if RAPID_TEST:
        with ctx_chdir(PROTYPE_DIR):
            tfdir = PROTYPE_DIR / ".terraform"
            if not tfdir.exists():
                subprocess.run(
                    "docker-compose run --rm devtools terraform init".split(" "),
                    check=True,
                )
            yield tfdir
    else:
        _tmp_path = tempfile.mkdtemp("dottf_dir")
        tmp_path = Path(_tmp_path)
        try:
            workdir = tmp_path / "terraform_dir"
            logging.info("workdir = %s", workdir)
            shutil.copytree(
                PROTYPE_DIR, workdir, ignore=shutil.ignore_patterns(".terraform")
            )

            with ctx_chdir(workdir):
                subprocess.run(
                    "docker-compose run --rm devtools terraform init".split(" "),
                    check=True,
                )
                tfdir = workdir / ".terraform"
                logging.debug("tfdir = %s", tfdir)
            yield tfdir
        finally:
            if KEEP_TMP:
                return
            try:
                shutil.rmtree(tmp_path, ignore_errors=True)
            except Exception:
                logging.warning("failed to rmtree %s", tmp_path, exc_info=True)


@pytest.fixture(scope="module")
def dottf_dir() -> Iterator[Optional[Path]]:
    with ctx_dottf_dir() as path:
        yield path


def test_prototype_ok(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir):
        subprocess.run("id".split(" "), check=True)
        subprocess.run("pwd".split(" "), check=True)
        subprocess.run("find .".split(" "), check=True)
        subprocess.run("docker-compose run --rm devtools".split(" "), check=True)

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 2
        assert sum("tfsec" in line for line in out_lines) == 2
        assert sum("tflint" in line for line in out_lines) == 2


def test_prototype_ok_no_module(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:

        shutil.rmtree(workdir / "eg_module", ignore_errors=False)
        os.remove(workdir / "use_eg_module.tf")

        subprocess.run("pwd".split(" "), check=True)
        subprocess.run("find .".split(" "), check=True)
        subprocess.run("docker-compose run --rm devtools".split(" "), check=True)

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 1
        assert sum("tfsec" in line for line in out_lines) == 1
        assert sum("tflint" in line for line in out_lines) == 1


def test_prototype_reinit(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir):
        subprocess.run(
            "docker-compose run --rm devtools validate".split(" "), check=True
        )

        subprocess.run(
            "docker-compose run --rm devtools terraform-reinit".split(" "), check=True
        )

        subprocess.run(
            "docker-compose run --rm devtools validate".split(" "), check=True
        )

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 4
        assert sum("tfsec" in line for line in out_lines) == 4
        assert sum("tflint" in line for line in out_lines) == 4


def test_prototype_env_vars(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:

        subprocess.run(
            "docker-compose run --rm devtools validate TFDIRS=".split(" "), check=True
        )

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 0
        assert sum("tfsec" in line for line in out_lines) == 0
        assert sum("tflint" in line for line in out_lines) == 0

        (workdir / "blank").mkdir()
        subprocess.run(
            "docker-compose run --rm -e TFDIRS=blank devtools validate".split(" "),
            check=True,
        )

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 1
        assert sum("tfsec" in line for line in out_lines) == 1
        assert sum("tflint" in line for line in out_lines) == 1

        subprocess.run(
            [
                *"docker-compose run --rm".split(" "),
                "-e",
                "TFDIRS_EXCLUDE=%/examples %/example %/eg_module",
                "devtools",
            ],
            check=True,
        )

        assert sum("No problems detected" in line for line in out_lines) == 1
        assert sum("tfsec" in line for line in out_lines) == 1
        assert sum("tflint" in line for line in out_lines) == 1


def test_prototype_fail_fmt(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:
        (workdir / "bad_fmt.tf").write_text(
            """
data "null_data_source" "values" {
  a = 1
  aaa = 1111
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
        assert "+++ new/bad_fmt.tf" in captured.out


def test_prototype_fail_validate(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:
        (workdir / "bad_validate.tf").write_text(
            """
resource "google_storage_bucket" "example" {
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
        assert "Missing required argument" in (captured.out + captured.err)


def test_prototype_fail_tfsec(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:
        (workdir / "bad_tfsec.tf").write_text(
            """
resource "google_storage_bucket" "example" {
  name     = "example"
  location = "EU"
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
        assert "Bucket has uniform bucket level access disabled." in captured.out


def test_prototype_fail_tflint(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:
        (workdir / "bad_tflint.tf").write_text(
            """
resource "google_project_iam_binding" "iam_binding" {
  project = "abc"
  role    = "def"
  members = [
    "first.last@example.com",
  ]
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
        assert "first.last@example.com is an invalid member format" in captured.out


def test_prototype_fallback(
    tmp_path: Path, dottf_dir: Optional[Path], capfd: CaptureFixture[str]
) -> None:
    with ctx_prototype(tmp_path, dottf_dir) as workdir:

        for file in [*glob.glob("*"), *glob.glob(".*")]:
            file_path = workdir / file
            if file.endswith("docker-compose.yaml"):
                continue
            logging.debug("removing %s", file)
            if file_path.is_dir():
                shutil.rmtree(workdir / file, ignore_errors=False)
            else:
                os.remove(file)

        subprocess.run(
            "docker-compose run --rm devtools validate".split(" "), check=True
        )

        captured = capfd.readouterr()
        with capfd.disabled():
            sys.stdout.write("captured.out:\n")
            sys.stdout.write(captured.out)
            sys.stderr.write("captured.err:\n")
            sys.stderr.write(captured.err)
        out_lines = captured.out.splitlines()
        assert sum("No problems detected" in line for line in out_lines) == 1
        assert sum("tfsec" in line for line in out_lines) == 1
        assert sum("tflint" in line for line in out_lines) == 1
