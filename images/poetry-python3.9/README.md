# Base image for Python 3.9 and the latest available version of Poetry

This image is intended to use for projects with Python 3.9 and Poetry.

Poetry is installed via `pip-tools`. Dependabot manages the updates
of Poetry and base python image.

## Generate requirements manually

To generate requirements manually run

```shell
docker compose build devtools
```

and then

```shell
docker compose run --rm devtools make generate-requirements
```

>**Note** If you want to force the generation of the requirements,
> update the timestamp of the `requirements.in`
>
> ```shell
> touch requirements.in
> ```
