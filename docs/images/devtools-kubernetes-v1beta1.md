# Kubernetes Development Tools

> [!IMPORTANT]
>
> The `devtools-kubernetes-v1beta1` image is deprecated and will be deleted. Use
> the `pallets`, `catalog-info` and `policy-bot` targets in
> [coopnorge/mage](https://github.com/coopnorge/mage) instead. For repositories
> with Helm or Kustomize manifests, use the Kubernetes validation in
> coopnorge/mage. See
> [#4456](https://github.com/coopnorge/engineering-docker-images/issues/4456).

- `OVERLAYS` environment variable: This is a space separated list of overlay
  directories to run validation checks on.

  Default: If this is not set any directory containing standard Kustomize files
  in it will be used.
