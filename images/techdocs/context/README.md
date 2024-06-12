This file contains instructions on using the `techdocs` image as you develop it.

```bash
# change into the image context directory
cd ./images/techdocs/context/

# build the image
docker compose build self

# run the default target
docker compose run --rm self

# get help
docker compose run --rm self help
```

