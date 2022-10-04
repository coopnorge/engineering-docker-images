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
def expected_techdocs_cli_version() -> bytes:
    return b"1.2.0"


def test_image_should_return_a_correct_techdocs_cli_version(
    docker_client: docker.DockerClient,
    build_image: Image,
    expected_techdocs_cli_version: bytes,
) -> None:
    actual_techdocs_cli_version = docker_client.containers.run(
        build_image.id,
        command="techdocs-cli --version",
        remove=True,
    )
    assert actual_techdocs_cli_version.startswith(expected_techdocs_cli_version)


@pytest.fixture(scope="session")
def expected_markdownlint_cli_version() -> bytes:
    return b"0.32.2"


def test_image_should_return_a_correct_markdownlint_cli_version(
    docker_client: docker.DockerClient,
    build_image: Image,
    expected_markdownlint_cli_version: bytes,
) -> None:
    actual_markdownlint_cli_version = docker_client.containers.run(
        build_image.id,
        command="markdownlint --version",
        remove=True,
    )
    assert actual_markdownlint_cli_version.startswith(expected_markdownlint_cli_version)
