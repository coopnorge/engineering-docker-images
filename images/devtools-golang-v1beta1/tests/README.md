

```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=devtools-golang-v1beta1 build


# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-golang-v1beta1:built \
poetry run pytest images/devtools-golang-v1beta1/tests
```
