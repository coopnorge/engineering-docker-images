# engineering-docker-images

## Layout

Dockerfiles for images are all located in the `images/` directory. Each image
has a subdirectory from which it's name will be derived.

## TODO

- [ ] Build Terraform and K8S
- [ ] Integration test images
- [ ] Scan images

## Developing

```bash
# build images
docker-compose build
# see available targets
docker-compose run --rm devtools make help
# validate
docker-compose run --rm devtools make validate VERBOSE=all
# run in watch mode
docker-compose run --rm devtools make watch
```

### without devtools

```bash
poetry install
make build validate test
```

### Useful commands

```bash
# run tests for only one image
make IMAGE_NAMES=devtools-terraform-v1beta1 build validate test
```
