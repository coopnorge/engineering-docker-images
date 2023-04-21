```bash
## Run commands from repo root

# Build image.
make IMAGE_NAMES=devtools-typescript-v1 build

# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-typescript-v1:built \
poetry run pytest images/devtools-typescript-v1/tests

# Run specific test
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-typescript-v1:built \
poetry run pytest 'images/devtools-typescript-v1/tests/test_image.py::test_alterations[docker-builds]'
```
