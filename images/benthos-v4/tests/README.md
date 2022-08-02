

```bash
## Run from repo root

# Build image.
make IMAGE_NAMES=benthos-v4 build

# Test image.
poetry run pytest images/benthos-v4/tests
```
