

```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=poetry-python3.10 build

# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/poetry-python3.10:built \
poetry run pytest images/poetry-python3.10/tests

# Run specific test
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/poetry-python3.10:built \
poetry run pytest images/poetry-python3.10/tests/test_image.py::test_runs
```
