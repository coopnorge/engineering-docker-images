# ...

## Developing

```bash
# build images
docker compose build
# see available targets
docker compose run --rm devtools help
# validate
docker compose run --rm devtools validate
# reinitalize terraform
docker compose run --rm devtools terraform-reinit
# upgrade terraform modules/providers
docker compose run --rm devtools terraform-upgrade
```
