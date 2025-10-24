import logging
import os
import pathlib
import re
from typing import List, Pattern

import docker
import pytest
from docker.models.images import Image


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    return docker.DockerClient.from_env()


@pytest.fixture(scope="session", autouse=True)
def build_image(
    docker_client: docker.DockerClient,
) -> Image:
    image, _ = docker_client.images.build(
        path="images/techdocs/context",
        rm=True,
    )
    return image


@pytest.fixture(scope="session")
def volumes() -> dict[str, dict[str, str]]:
    current_directory = pathlib.Path(__file__).parent.resolve()
    prototype = os.path.abspath(f"{current_directory}/prototype/")
    return {prototype: {"bind": "/srv/workspace", "mode": "rw"}}


@pytest.mark.parametrize(
    "cli_command,expected_ouput",
    [
        ("techdocs-cli --version", b"1."),
        ("markdownlint --version", b"0."),
        ("vale --version", b"vale version 3."),
        ("yq --version", b"yq (https://github.com/mikefarah/yq/) version v4."),
    ],
)
def test_image_should_return_a_correct_cli_tool_version(
    docker_client: docker.DockerClient,
    build_image: Image,
    cli_command: str,
    expected_ouput: bytes,
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command=cli_command,
        remove=True,
    )
    assert actual_output.startswith(expected_ouput)


def test_lint(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command="lint MARKDOWN_FILES=docs/",
        volumes=volumes,
        remove=True,
    )
    assert b"markdownlint --config=../markdownlint.yaml docs/\n" in actual_output


def test_vale_sync(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command="vale-sync",
        volumes=volumes,
        remove=True,
    )
    assert b"vale sync" in actual_output


def test_linguistics_check(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command='linguistics-check MARKDOWN_FILES="README.md docs/index.md"',
        volumes=volumes,
        remove=True,
    )
    assert (
        b"vale README.md docs/index.md\n\xe2\x9c\x94 \x1b[31m0 errors\x1b[0m, \x1b[33m0 warnings\x1b[0m and \x1b[34m0 suggestions\x1b[0m in 2 files.\n"
        in actual_output
    )


def test_test_validate(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command='validate MARKDOWN_FILES="README.md docs/index.md"',
        volumes=volumes,
        remove=True,
    )
    assert (
        b"prettier --check --config ../.prettierrc README.md docs/index.md\n"
        in actual_output
    )
    assert (
        b"markdownlint --config=../markdownlint.yaml README.md docs/index.md\n"
        in actual_output
    )
    assert (
        b"vale README.md docs/index.md\n\xe2\x9c\x94 \x1b[31m0 errors\x1b[0m, \x1b[33m0 warnings\x1b[0m and \x1b[34m0 suggestions\x1b[0m in 2 files.\n"
        in actual_output
    )


@pytest.fixture()
def wrong_volumes() -> dict[str, dict[str, str]]:
    current_directory = pathlib.Path(__file__).parent.resolve()
    prototype = os.path.abspath(f"{current_directory}/prototype/")
    return {prototype: {"bind": "/srv/bad-workspace", "mode": "rw"}}


def test_validate_wrong_pwd(
    docker_client: docker.DockerClient,
    build_image: Image,
    wrong_volumes: dict[str, dict[str, str]],
) -> None:
    with pytest.raises(Exception) as excinfo:
        docker_client.containers.run(
            build_image.id,
            command='validate MARKDOWN_FILES="README.md docs/index.md"',
            volumes=wrong_volumes,
            working_dir="/srv/bad-workspace",
            remove=True,
        )

    assert (
        "Error: Update docker compose working directory and volume to /srv/workspace"
        in str(excinfo.value)
    )


def test_build(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command='build SITE_NAME=example REPO_NAME=example/test REPO_URL="http://github.com/example/test" EDIT_URL="edit/main/docs" GITHUB_TOKEN="fake-token"',
        volumes=volumes,
        remove=True,
    )
    assert (
        b"info: Successfully generated docs from /srv/workspace into /srv/workspace/site using local mkdocs"
        in actual_output
    )


@pytest.mark.parametrize(
    ["cli_command", "expected_patterns", "unexpected_patterns"],
    [
        pytest.param(
            ["lint-fix", "MARKDOWN_FILES=README.md docs/index.md"],
            [re.compile("markdownlint.*--fix.*README.md")],
            [],
            id="test-lint-fix",
        ),
        pytest.param(
            ["validate-fix", "MARKDOWN_FILES=README.md docs/index.md"],
            [re.compile("markdownlint.*--fix.*README.md")],
            [],
            id="test-validate-fix",
        ),
    ],
)
def test_command_output(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
    cli_command: List[str],
    expected_patterns: List[Pattern[str]],
    unexpected_patterns: List[Pattern[str]],
) -> None:
    logging.debug("cli_command = %s", cli_command)
    actual_output = docker_client.containers.run(
        build_image.id,
        command=cli_command,
        volumes=volumes,
        remove=True,
    )
    logging.debug("actual_output = \n%s", actual_output.decode("utf-8"))
    for expected_pattern in expected_patterns:
        assert len(expected_pattern.findall(actual_output.decode("utf-8"))) >= 1
    for unexpected_pattern in unexpected_patterns:
        assert len(unexpected_pattern.findall(actual_output.decode("utf-8"))) == 0
