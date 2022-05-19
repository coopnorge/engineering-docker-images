

```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=devtools-kubernetes-v1beta1 build


# Test image.
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-kubernetes-v1beta1:built \
poetry run pytest images/devtools-kubernetes-v1beta1/tests
```
