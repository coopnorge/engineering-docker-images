# Base image for Python 3.10 and the latest available version of pip-tools

This image is intended to use for projects with Python 3.10 and Poetry.
`pip-tools` is installed via `pip-tools`. Dependabot manages the updates
of Poetry and base python image.

## Generate `requirements.txt`

1. Build `pip-tools` service with Docker Compose

   ```shell
   docker compose build devtools
   ```

> **Optional:** update a timestamp of `requirements.in`
>
> ```shell
> touch requirements.txt
> ```

2.2 Re-generate `requirements.txt`

    ```
    docker compose run --rm pip-tools make generate-requirements
    ``

## Running tests


```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=pip-tools-python3.10 build

# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/pip-tools-python3.10:built \
poetry run pytest images/poetry-python3.10/tests

# Run specific test
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/pip-tools-python3.10:built \
poetry run pytest images/pip-tools-python3.10/tests/test_image.py::test_runs
```
