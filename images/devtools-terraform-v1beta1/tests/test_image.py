import glob
import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path, PurePath
from typing import (
    Callable,
    Dict,
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
PROTYPE_DIR = TEST_DIR / "prototype"
VAR_XDG_CACHE_DIR = TEST_DIR / "var" / "XDG_CACHE_DIR"

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


def envargs_from_dict(env_args: Optional[Dict[str, str]] = None) -> List[str]:
    if env_args is None:
        return []
    return sum(
        [["-e", f"{key}={value}"] for key, value in env_args.items()],
        [],
    )


@contextmanager
def ctx_prototype(
    tmp_path: Path,
    cache_dir: Optional[Path],
) -> Generator[Path, None, None]:
    logging.debug("RAPID_TEST = %s", RAPID_TEST)
    workdir = tmp_path / "base"
    logging.info("workdir = %s, cache_dir = %s", workdir, cache_dir)
    shutil.copytree(
        PROTYPE_DIR,
        workdir,
        ignore=shutil.ignore_patterns(".terraform", ".terraform.lock.hcl"),
    )

    with ctx_chdir(workdir):
        dotenv_vars = {"COMPOSE_PROJECT_NAME": "devtools-terraform-reinit"}
        if cache_dir is not None:
            dotenv_vars["_XDG_CACHE_DIR"] = f"{cache_dir}"
        (workdir / ".env").write_text(
            "\n".join([f"{key}={value}" for key, value in dotenv_vars.items()])
        )

        subprocess.run(
            "docker compose down -v".split(" "),
            check=True,
        )
        run_cmd = "docker compose run --rm".split(" ") + [
            "devtools",
            "bash",
            "-c",
            textwrap.dedent("""
                    find /srv/workspace/.terraform/
                    find ~/.cache/
                    """),
        ]
        logging.debug("running %s", shlex.join(run_cmd))
        subprocess.run(run_cmd, check=True)
        yield workdir


@pytest.fixture(scope="module")
def cache_dir() -> Generator[Optional[Path], None, None]:
    if RAPID_TEST:
        VAR_XDG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        yield VAR_XDG_CACHE_DIR
    else:
        # yield None
        _tmp_path = tempfile.mkdtemp("-devtools-terraform-cache")
        tmp_path = Path(_tmp_path)
        try:
            yield tmp_path
        finally:
            if KEEP_TMP:
                return
            try:
                shutil.rmtree(tmp_path, ignore_errors=True)
            except Exception:
                logging.warning("failed to rmtree %s", tmp_path, exc_info=True)


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


def devtools_cmd(
    args: Optional[List[str]] = None, /, *, envargs: Optional[Dict[str, str]] = None
) -> List[str]:
    if args is None:
        args = []
    cmd = [
        "docker",
        "compose",
        "run",
        "--rm",
        *envargs_from_dict(envargs),
        "devtools",
        *args,
    ]
    logging.debug("will run: %s", shlex.join(cmd))
    return cmd


def test_prototype_ok(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir if RAPID_TEST else None):
        subprocess.run("id".split(" "), check=True)
        subprocess.run("pwd".split(" "), check=True)
        subprocess.run("find .".split(" "), check=True)
        subprocess.run(devtools_cmd(), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 7
        assert sum("tflint" in line for line in cap.out_lines) == 2

        subprocess.run(devtools_cmd(["maker", "validate"]), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 7
        assert sum("tflint" in line for line in cap.out_lines) == 2


def test_prototype_nocache(
    tmp_path: Path,
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, None):
        subprocess.run("id".split(" "), check=True)
        subprocess.run("pwd".split(" "), check=True)
        subprocess.run("find .".split(" "), check=True)
        subprocess.run(devtools_cmd(envargs={"TF_PLUGIN_CACHE_DIR": ""}), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 7
        assert sum("tflint" in line for line in cap.out_lines) == 2


def test_prototype_ok_no_module(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir if RAPID_TEST else None) as workdir:
        shutil.rmtree(workdir / "eg_module", ignore_errors=False)
        os.remove(workdir / "use_eg_module.tf")

        subprocess.run("pwd".split(" "), check=True)
        subprocess.run("find .".split(" "), check=True)
        subprocess.run(devtools_cmd(), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 6
        assert sum("tflint" in line for line in cap.out_lines) == 1


def test_prototype_reinit_upgrade(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir):
        subprocess.run(devtools_cmd(["validate"]), check=True)

        subprocess.run(devtools_cmd(["terraform-reinit"]), check=True)

        subprocess.run(devtools_cmd(["terraform-upgrade"]), check=True)

        subprocess.run(devtools_cmd(["validate"]), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 14
        assert sum("tflint" in line for line in cap.out_lines) == 4


def test_prototype_env_vars(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        subprocess.run(devtools_cmd(["validate", "TFDIRS="]), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 6
        assert sum("tflint" in line for line in cap.out_lines) == 1

        (workdir / "blank").mkdir()
        subprocess.run(
            devtools_cmd(["validate"], envargs={"TFDIRS": "blank"}),
            check=True,
        )

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 6
        assert sum("tflint" in line for line in cap.out_lines) == 1

        subprocess.run(
            devtools_cmd(
                envargs={"TFDIRS_EXCLUDE": "%/examples %/example %/eg_module"}
            ),
            check=True,
        )

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 6
        assert sum("tflint" in line for line in cap.out_lines) == 1


def test_dir_exclusion_behavior(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir):  # as workdir:
        # default values
        subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert (
            sum("TFDIRS_EXCLUDE=%/examples %/example" == line for line in cap.out_lines)
            == 1
        )
        assert sum("TFDIRS=. ./eg_module" == line for line in cap.out_lines) == 1

        # TFDIRS_EXCLUDE override using env var
        subprocess.run(
            devtools_cmd(
                ["validate"], envargs={"TFDIRS_EXCLUDE": "./eg_exclusion_module"}
            ),
        )
        cap = Captured.from_capfd(capfd)
        assert (
            sum(
                "TFDIRS_EXCLUDE=./eg_exclusion_module" == line for line in cap.out_lines
            )
            == 1
        )
        assert (
            sum(
                "TFDIRS=. ./eg_module ./example ./examples" == line
                for line in cap.out_lines
            )
            == 1
        )

        # TFDIRS_EXCLUDE override using command line
        subprocess.run(
            devtools_cmd(["validate", "TFDIRS_EXCLUDE=./eg_exclusion_module"]),
        )
        cap = Captured.from_capfd(capfd)
        assert (
            sum(
                "TFDIRS_EXCLUDE=./eg_exclusion_module" == line for line in cap.out_lines
            )
            == 1
        )
        assert (
            sum(
                "TFDIRS=. ./eg_module ./example ./examples" == line
                for line in cap.out_lines
            )
            == 1
        )

        # check if TFDIRS_EXCLUDE is applied if TFDIRS is set via env var
        subprocess.run(
            devtools_cmd(["validate"], envargs={"TFDIRS": "./ ./example ./examples"}),
        )
        cap = Captured.from_capfd(capfd)
        assert sum("TFDIRS=./" == line for line in cap.out_lines) == 1
        assert (
            sum("TFDIRS_EXCLUDE=%/examples %/example" == line for line in cap.out_lines)
            == 1
        )

        # check if TFDIRS_EXCLUDE is applied if TFDIRS is set via command line
        subprocess.run(
            devtools_cmd(["validate", "TFDIRS=./ ./example ./examples"]),
        )
        cap = Captured.from_capfd(capfd)
        assert sum("TFDIRS=./" == line for line in cap.out_lines) == 1
        assert (
            sum("TFDIRS_EXCLUDE=%/examples %/example" == line for line in cap.out_lines)
            == 1
        )


def test_prototype_fail_fmt(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        (workdir / "bad_fmt.tf").write_text("""
data "null_data_source" "values" {
  a = 1
  aaa = 1111
}
""")
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(devtools_cmd(), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("+++ new/bad_fmt.tf" in line for line in cap.out_lines) == 1


def write_google_versions_tf(workdir: Path) -> None:
    (workdir / "versions.tf").write_text("""
# https://www.terraform.io/docs/language/settings/index.html
# https://www.terraform.io/docs/language/expressions/version-constraints.html
terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.4"
    }
  }
  required_version = "~> 1.0"
}
""")


def test_prototype_fail_validate(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        write_google_versions_tf(workdir)
        (workdir / "bad_validate.tf").write_text("""
resource "google_storage_bucket" "example" {
}
""")
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert "Missing required argument" in (cap.out + cap.err)


def test_prototype_trivy_failed_and_skip(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        write_google_versions_tf(workdir)
        (workdir / "bad_tfsec.tf").write_text("""
resource "google_storage_bucket" "example" {
  name     = "example"
  location = "EU"
}
""")
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert (
            sum(
                "Bucket has uniform bucket level access disabled." in line
                for line in cap.out_lines
            )
            == 1
        )
        assert sum("Failures: " in line for line in cap.out_lines) == 1

        (workdir / ".tfsec-ignore").touch(exist_ok=True)
        (workdir / "eg_module" / ".tfsec-ignore").touch(exist_ok=True)
        subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert sum("Failures: " in line for line in cap.out_lines) == 0


def test_prototype_fail_tflint(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        write_google_versions_tf(workdir)
        (workdir / "bad_tflint.tf").write_text("""
resource "google_project_iam_binding" "iam_binding" {
  project = "abc"
  role    = "def"
  members = [
    "first.last@example.com",
  ]
}
""")
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert "invalid value for members.0" in cap.all()


def test_prototype_tfdocs_fail(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        (workdir / "terraform-docs.yml").write_text("""
formatter: "markdown table"
output:
  file: "README.md"
  mode: replace
  template: |-
    <!-- BEGIN_TF_DOCS -->
    {{ .Content }}
    <!-- END_TF_DOCS -->
""")
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(devtools_cmd(), check=True)
        cap = Captured.from_capfd(capfd)
        assert (
            sum("Error: README.md is out of date" in line for line in cap.all_lines)
            == 1
        )


def test_prototype_fallback(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
) -> None:
    with ctx_prototype(tmp_path, cache_dir) as workdir:
        for file in [*glob.glob("*"), *glob.glob(".*")]:
            file_path = workdir / file
            if file.endswith("docker-compose.yaml"):
                continue
            logging.debug("removing %s", file)
            if file_path.is_dir():
                shutil.rmtree(workdir / file, ignore_errors=False)
            else:
                os.remove(file)

        subprocess.run(devtools_cmd(["validate"]), check=True)

        cap = Captured.from_capfd(capfd)
        assert sum("trivy" in line for line in cap.out_lines) == 6
        assert sum("tflint" in line for line in cap.out_lines) == 1


@pytest.mark.parametrize(
    ["mutators", "env", "commands", "success", "matchers"],
    [
        pytest.param(
            [],
            {},
            [
                "terraform-reinit".split(),
                "terraform-relock".split(),
            ],
            True,
            [("Obtained hashicorp/null checksums for darwin_amd64", True)],
            id="relock",
        ),
        pytest.param(
            [],
            {"TF_LOCK_PLATFORMS": "linux_arm64"},
            [
                "terraform-reinit".split(),
                "terraform-relock".split(),
            ],
            True,
            [
                ("Obtained hashicorp/null checksums for darwin_amd64", False),
                ("Obtained hashicorp/null checksums for linux_arm64", True),
            ],
            id="relock-selected",
        ),
    ],
)
def test_runs(
    tmp_path: Path,
    cache_dir: Optional[Path],
    capfd: CaptureFixture[str],
    mutators: Iterable[Callable[[Path], None]],
    env: Dict[str, str],
    commands: Iterable[List[str]],
    success: bool,
    matchers: Iterable[Tuple[str, bool]],
) -> None:
    with ExitStack() as xstack:
        workdir = xstack.enter_context(ctx_prototype(tmp_path, cache_dir))
        for mutator in mutators:
            mutator(workdir)
        if not success:
            xstack.enter_context(pytest.raises(subprocess.CalledProcessError))
        for command in commands:
            subprocess.run(devtools_cmd(command, envargs=env), check=True)
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
