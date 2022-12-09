# Backstage TechDocs Engineering Image

The image contains the full suite of tools required to publish a TechDocs site
in Inventory.

## Usage

The image is designed to run in a repository containing TechDocs.

### Docker compose configuration

Add a `docker-compose.yaml` file to the repository.

```yaml
---
services:
  techdocs:
    build:
      context: docker-compose
      dockerfile: Dockerfile
      target: techdocs
    working_dir: /content
    environment:
      GCLOUD_PROJECT: ${GCLOUD_PROJECT:-}
    volumes:
      - .:/content
      - ${XDG_CACHE_HOME:-xdg-cache-home}:/root/.cache
    secrets:
      - source: google-application-credentials
        target: /root/.config/gcloud/application_default_credentials.json
    ports:
      - "127.0.0.1:3000:3000/tcp"
      - "127.0.0.1:8000:8000/tcp"
    command: serve
secrets:
  google-application-credentials:
    file: $GOOGLE_APPLICATION_CREDENTIALS
volumes:
  xdg-cache-home: { }
  nothing: { }
```

### Running a preview site

```bash
docker compose up techdocs
```

Open your browser at http://localhost:3000/docs/default/component/local/

###  List targets

```bash
docker compose run --rm techdocs help
```
