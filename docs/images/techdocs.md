# Backstage TechDocs Engineering Image

The image contains the full suite of tools required to publish a TechDocs site
in Inventory.

## Usage

The image is designed to run in a repository containing TechDocs.

### Docker compose configuration

Add a `devtools/techdocs.yaml` file to the repository.

```yaml title="devtools/techdocs.yaml"
services:
  techdocs:
    build:
      dockerfile: techdocs.Dockerfile
    working_dir: /srv/workspace
    environment:
      GOOGLE_APPLICATION_CREDENTIALS: ${GOOGLE_APPLICATION_CREDENTIALS:-}
      GCLOUD_PROJECT: ${GCLOUD_PROJECT:-}
    volumes:
      - ../:/srv/workspace:z
      - ${XDG_CACHE_HOME:-xdg-cache-home}:/root/.cache
      - $HOME/.config/gcloud:/root/.config/gcloud
      - ${GOOGLE_APPLICATION_CREDENTIALS:-nothing}:${GOOGLE_APPLICATION_CREDENTIALS:-/tmp/empty-GOOGLE_APPLICATION_CREDENTIALS}
    ports:
      - "127.0.0.1:3000:3000/tcp"
      - "127.0.0.1:8000:8000/tcp"
    command: serve
volumes:
  xdg-cache-home: { }
  nothing: { }
```

```yaml title="docker-compose.yaml"
include:
  - devtools/techdocs.yaml
```

```Dockerfile title="devtools/Dockerfile"
FROM ghcr.io/coopnorge/engineering-docker-images/e0/techdocs:latest@sha256:68ce8f1b1745d587dbd542b1e8d4974eacf513ea2adffa1d566e76cca071417c
```

### Running a preview site

```bash
docker compose up techdocs
```

Open your browser at <http://localhost:3000/docs/default/component/local/>

### List targets

```bash
docker compose run --rm techdocs help
```

## Writing documentation

### Toolbox

- [TechDocs](https://backstage.io/docs/features/techdocs/)
- [MKDocs](https://www.mkdocs.org/)

  MKDocs Plugins:

  - [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
  - [MkDocs Awesome Pages]
  - [EZLinks](https://github.com/orbikm/mkdocs-ezlinks-plugin)
  - [Kroki](https://kroki.io/)
  - [Table Reader]

- [markdownlint](https://github.com/DavidAnson/markdownlint#configuration)
- [Vale](https://vale.sh/)

### Render table data from files

[Table Reader] can render data from `.csv`, `.fwf`, `.json`, `.xlsx`, `.yaml`
and `.tsv` files.

To load a `.csv` file use:

<code>\{\{ read_csv('path_to_table.csv') \}\}</code>

The `path_to_table.csv` is relative to the `docs/` directory in the repository.

## Customize navigation

See [MkDocs Awesome Pages]

## Ignoring rules

Both markdownlint and Vale define rules for style and spelling. Sometimes rules
needs to be broken.

markdownlint rules can be controlled by line and for sections. For more
information see the official [markdownlint documentation][markdownlint].

- Disable all rules: `<!-- markdownlint-disable -->`
- Enable all rules: `<!-- markdownlint-enable -->`
- Disable all rules for the current line: `<!-- markdownlint-disable-line -->`
- Disable all rules for the next line: `<!-- markdownlint-disable-next-line -->`
- Disable one or more rules by name: `<!-- markdownlint-disable MD001 MD005 -->`
- Enable one or more rules by name: `<!-- markdownlint-enable MD001 MD005 -->`
- Disable one or more rules by name for the current line:
  `<!-- markdownlint-disable-line MD001 MD005 -->`
- Disable one or more rules by name for the next line:
  `<!-- markdownlint-disable-next-line MD001 MD005 -->`
- Capture the current rule configuration: `<!-- markdownlint-capture -->`
- Restore the captured rule configuration: `<!-- markdownlint-restore -->`

Vale rules case be controlled by section, for more information see the official
[Vale documentation](https://vale.sh/docs/topics/config/#markdown-amp-html).

```md title="markdown.md"
<!-- vale off -->

This is some text

more text here...

<!-- vale on -->

<!-- vale Style.Rule = NO -->

This is some text

<!-- vale Style.Rule = YES -->
```

[MkDocs Awesome Pages]: https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin/#features
[Table Reader]: https://timvink.github.io/mkdocs-table-reader-plugin/
[markdownlint]: https://github.com/DavidAnson/markdownlint#configuration
