

```bash
## Run from repo root

# build image
make IMAGE_NAMES=devtools-terraform-v1beta1 build

# test image
IMAGE_UNDER_TEST=ocreg.invalid/coopnorge/engineering/image/devtools-terraform-v1beta1:built \
RAPID_TEST=1 \
poetry run pytest images/devtools-terraform-v1beta1/tests
```
