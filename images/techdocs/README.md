# Backstage TechDocs Engineering Image

The image contains the full suite of tools required to publish a TechDocs site
in Inventory.

## Usage

### Running a development server

```bash
docker run -v $(pwd):/content -p 3000:3000 ghcr.io/coopnorge/engineering-docker-images/e0/techdocs techdocs-cli serve --no-docker -v
```

### Other targets

```bash
docker run -v $(pwd):/content ghcr.io/coopnorge/engineering-docker-images/e0/techdocs help
```
