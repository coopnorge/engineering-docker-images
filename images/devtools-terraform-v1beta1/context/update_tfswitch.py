#!/usr/bin/env python
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.request import urlopen

SCRIPT_DIR_PATH = Path(__file__).parent


def lock_latest() -> None:
    """
    Locks tfswitch to the latest version.
    """
    release_url = (
        "https://api.github.com/repos/warrensbox/terraform-switcher/releases/latest"
    )

    with urlopen(release_url) as io:
        release = json.load(io)

    logging.debug(f"release = %s", release)

    latest_version = release["tag_name"]
    logging.info(f"{latest_version=}")

    checksums_assets = next(
        asset for asset in release["assets"] if asset["name"].endswith("_checksums.txt")
    )

    checksums_url: str = checksums_assets["browser_download_url"]
    checksums_filename: str = checksums_assets["name"]
    checksums_path = SCRIPT_DIR_PATH / checksums_filename
    logging.debug(f"{checksums_url = } {checksums_filename = } {checksums_path = }")

    # Clean old checksum files.

    for checksum_file in SCRIPT_DIR_PATH.glob("*_checksums.txt"):
        logging.info(f"removing {checksum_file = }")
        os.unlink(checksum_file)

    # Dowload latest checksum file
    with urlopen(checksums_url) as rio, checksums_path.open("wb+") as lio:
        logging.info(f"downloading {checksums_url = } to {checksums_path = }")
        shutil.copyfileobj(rio, lio)

    # Update version in dockerfile
    dockerfile = SCRIPT_DIR_PATH / "Dockerfile"
    dockefile_content = dockerfile.read_bytes().decode("utf-8")
    dockefile_content = re.sub(
        r"tfswitcher_version=\S+",
        f"tfswitcher_version={latest_version}",
        dockefile_content,
        re.MULTILINE | re.DOTALL,
    )
    dockerfile.write_bytes(dockefile_content.encode("utf-8"))


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("PYLOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    lock_latest()


if __name__ == "__main__":
    main()
