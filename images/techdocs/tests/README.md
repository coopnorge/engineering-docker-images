## Techdocs tests

```bash
## Run commands from repo root

# Build image.
make IMAGE_NAMES=techdocs build

# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/techdocs:built \
poetry run pytest images/techdocs/tests

# Run specific test
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/techdocs:built \
poetry run pytest 'images/techdocs/tests/test_image.py::test_command_output'
```
