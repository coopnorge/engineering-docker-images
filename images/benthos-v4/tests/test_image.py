import logging
from contextlib import ExitStack
from pathlib import Path
from typing import Iterable, List, Tuple, Union

import docker
import docker.errors
import pytest
from docker.models.images import Image

TEST_DIR = Path(__file__).parent.absolute()
IMAGE_CONTEXT_DIR = (TEST_DIR.parent / "context").absolute()


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    return docker.DockerClient.from_env()


@pytest.fixture(scope="session", autouse=True)
def build_image(
    docker_client: docker.DockerClient,
) -> Image:
    image, _ = docker_client.images.build(
        path=f"{IMAGE_CONTEXT_DIR}",
        quiet=False,
    )
    logging.debug("image = %s, image.id = %s", image, image.id)
    return image


@pytest.mark.parametrize(
    ["command", "success", "matchers"],
    [
        pytest.param(
            "--version",
            True,
            [("Version: v4.", True)],
            id="correct-version",
        ),
    ],
)
def test_runs(
    docker_client: docker.DockerClient,
    build_image: Image,
    command: Union[List[str], str],
    success: bool,
    matchers: Iterable[Tuple[str, bool]],
) -> None:
    with ExitStack() as xstack:
        if not success:
            xstack.enter_context(pytest.raises(docker.errors.ContainerError))

        output: bytes = docker_client.containers.run(
            build_image.id,
            command=command,
            remove=True,
        )

        logging.debug("output = %s", output)
        output_str = output.decode()

        for match_string, match_positive in matchers:
            if match_positive:
                assert (
                    match_string in output_str
                ), f"did not find {match_string} in output ...\n{output_str}"
            else:
                assert (
                    match_string not in output_str
                ), f"found {match_string} in output\n{output_str}"
