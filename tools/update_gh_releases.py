#!/usr/bin/env python
from dataclasses import dataclass
import fnmatch
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.request import urlopen

SCRIPT_DIR_PATH = Path(__file__).parent.parent


@dataclass
class Replacer:
    file: Path
    replace: str

    def apply(self, latest_version: str) -> None:
        file = SCRIPT_DIR_PATH / self.file
        # Update version in dockerfile
        logging.info(f"replace {file = !r} {latest_version = !r} {self.replace = !r}")
        file_content = file.read_bytes().decode("utf-8")
        file_content = re.sub(
            self.replace.format(latest_version=r"[0-9a-zA-Z.]+"),
            self.replace.format(latest_version=latest_version),
            file_content,
            re.MULTILINE | re.DOTALL,
        )
        file.write_bytes(file_content.encode("utf-8"))


@dataclass
class LockAsset:
    remote_glob: str
    output_name: str


def lock_latest(
    project: str, lock_assets: Iterable[LockAsset], replacers: Iterable[Replacer]
) -> None:
    """
    Locks tfswitch to the latest version.
    """
    release_url = f"https://api.github.com/repos/{project}/releases/latest"

    with urlopen(release_url) as io:
        release = json.load(io)

    logging.debug("release = %s", release)

    latest_version: str = release["tag_name"]
    latest_version = latest_version.removeprefix("v")
    logging.info(f"{latest_version=}")

    # get remote
    remote_assets: List[Dict[str, Any]] = []
    for remote_asset in release["assets"]:
        for lock_asset in lock_assets:
            if fnmatch.fnmatch(remote_asset["name"], lock_asset.remote_glob):
                remote_asset["local_filename"] = (
                    SCRIPT_DIR_PATH
                    / lock_asset.output_name.format(latest_version=latest_version)
                )
                remote_assets.append(remote_asset)

    # Remove local
    for lock_asset in lock_assets:
        for lock_asset_path in SCRIPT_DIR_PATH.glob(
            lock_asset.output_name.format(latest_version="*")
        ):
            logging.info(f"removing {lock_asset_path = }")
            os.unlink(lock_asset_path)

    # fetch remote
    for remote_asset in remote_assets:
        remote_asset_url: str = remote_asset["browser_download_url"]
        remote_asset_local_filename = remote_asset["local_filename"]
        logging.debug(f"{remote_asset_url = } {remote_asset_local_filename = }")

        # Dowload latest checksum file
        with urlopen(remote_asset_url) as rio, open(
            remote_asset_local_filename, "wb+"
        ) as lio:
            logging.info(
                f"downloading {remote_asset_url = } to {remote_asset_local_filename = }"
            )
            shutil.copyfileobj(rio, lio)

    for replacer in replacers:
        replacer.apply(latest_version)


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

    lock_latest(
        "bufbuild/buf",
        [
            LockAsset(
                "sha256.txt",
                "images/devtools-golang-v1beta1/context/buf-{latest_version}.sha256sum",
            )
        ],
        [
            Replacer(
                Path("images/devtools-golang-v1beta1/context/Dockerfile"),
                "buf_version={latest_version}",
            ),
            Replacer(
                Path("images/devtools-golang-v1beta1/context/buf-fetch.sh"),
                "FILE_VERSION:={latest_version}",
            ),
        ],
    )


if __name__ == "__main__":
    main()
