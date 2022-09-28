This file contains instructions on using the devtools-golang image as you develop it.

```bash
# change into the image context directory
cd ./images/devtools-golang-v1beta1/context/

# build the image
docker compose build

# run the default target
docker compose run --rm devtools

# run the default target
docker compose run --rm devtools watch

# build and validate the OCI image
docker compose run --rm -e APP_DOCKERFILE=build/package/Dockerfile.example devtools validate VERBOSE=all; \
cat var/oci_images/stage-runtime.oci.tar | docker image load
docker run --rm -it ocreg.invalid/prototype:latest 1 2 3
docker image save ocreg.invalid/prototype:latest | dlayer

# pushing OCI images
gcloud --verbosity debug auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://europe-docker.pkg.dev
docker compose run --rm -e APP_DOCKERFILE=build/package/Dockerfile.example devtools publish VERBOSE=all OCI_REF_NAMES=europe-docker.pkg.dev/sandbox-iwan-aucamp-e332/common-docker/golang-devtools-prototype

# devtools shell
docker compose run --rm devtools bash
maker build
maker push-oci APP_DOCKERFILE=build/package/Dockerfile.example OCI_REF_NAMES=europe-docker.pkg.dev/sandbox-iwan-aucamp-e332/common-docker/golang-devtools-prototype skip=oci-context

# other commands
docker compose run --rm devtools help
```
