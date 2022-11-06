import os
import pathlib

import docker
import pytest
from docker.models.images import Image


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    return docker.DockerClient(base_url="unix:///var/run/docker.sock")


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
    return {prototype: {"bind": "/content", "mode": "rw"}}


@pytest.mark.parametrize(
    "cli_command,expected_ouput",
    [
        ("techdocs-cli --version", b"1."),
        ("markdownlint --version", b"0.32."),
        ("vale --version", b"vale version v2."),
        ("yq --version", b"yq (https://github.com/mikefarah/yq/) version 4."),
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
        command="lint DOCS_DIR=docs/",
        volumes=volumes,
        remove=True,
    )
    assert b"markdownlint --config=../markdownlint.yaml docs/\n" in actual_output


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
        actual_output
        == b"vale README.md docs/index.md\n\xe2\x9c\x94 \x1b[31m0 errors\x1b[0m, \x1b[33m0 warnings\x1b[0m and \x1b[34m0 suggestions\x1b[0m in 2 files.\n"
    )


def test_test_validate(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command='validate DOCS_DIR="docs/" MARKDOWN_FILES="README.md docs/index.md"',
        volumes=volumes,
        remove=True,
    )
    assert b"markdownlint --config=../markdownlint.yaml docs/\n" in actual_output
    assert (
        b"vale README.md docs/index.md\n\xe2\x9c\x94 \x1b[31m0 errors\x1b[0m, \x1b[33m0 warnings\x1b[0m and \x1b[34m0 suggestions\x1b[0m in 2 files.\n"
        in actual_output
    )


def test_build(
    docker_client: docker.DockerClient,
    build_image: Image,
    volumes: dict[str, dict[str, str]],
) -> None:
    actual_output = docker_client.containers.run(
        build_image.id,
        command='build REPO_NAME=example/test REPO_URL="http://github.com/example/test" EDIT_URL="edit/main/docs"',
        volumes=volumes,
        remove=True,
    )
    assert (
        b"info: Successfully generated docs from /content into /content/site using local mkdocs"
        in actual_output
    )
