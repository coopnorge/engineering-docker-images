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


@pytest.mark.parametrize(
    "cli_command,expected_ouput",
    [
        ("techdocs-cli --version", b"1.2.0"),
        ("markdownlint --version", b"0.32.2"),
        ("vale --version", b"vale version v2.20.2"),
        ("yq --version", b"yq (https://github.com/mikefarah/yq/) version 4.28.1"),
    ],
)
def test_image_should_return_a_correct_techdocs_cli_version(
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
