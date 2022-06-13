

```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=devtools-terraform-v1beta1 build


# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-terraform-v1beta1:built \
poetry run pytest images/devtools-terraform-v1beta1/tests

# Run specific test
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-terraform-v1beta1:built \
poetry run pytest images/devtools-terraform-v1beta1/tests/test_image.py::test_runs

# Rapid test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-terraform-v1beta1:built \
RAPID_TEST=1 \
poetry run pytest images/devtools-terraform-v1beta1/tests
```
