# ...

## Developing

```bash
# build images
docker-compose build
# see available targets
docker-compose run --rm devtools help
# validate
docker-compose run --rm devtools validate build VERBOSE=all
# run in watch mode
docker-compose run --rm devtools watch
```
