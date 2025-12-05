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
        path="images/poetry-python3.9/context",
        rm=True,
    )
    return image


@pytest.fixture(scope="session")
def expected_poetry_version() -> bytes:
    return b"Poetry (version 2."


@pytest.fixture(scope="session")
def expected_python_version() -> bytes:
    return b"Python 3.9"


def test_image_should_return_a_correct_python_version(
    docker_client: docker.DockerClient,
    build_image: Image,
    expected_poetry_version: bytes,
    expected_python_version: bytes,
) -> None:
    actual_poetry_version = docker_client.containers.run(
        build_image.id,
        command="poetry --version",
        remove=True,
    )
    assert actual_poetry_version.startswith(expected_poetry_version)
    actual_python_version = docker_client.containers.run(
        build_image.id,
        command="python --version",
        remove=True,
    )
    assert actual_python_version.startswith(expected_python_version)
