# Kubernetes Development Tools

> [!IMPORTANT]
>
> The `devtools-kubernetes-v1beta1` image is deprecated and will be deleted. Use
> the targets and reusable workflows in
> [coopnorge/mage](https://github.com/coopnorge/mage) instead. Progress is
> tracked in
> [engineering-docker-images#4456](https://github.com/coopnorge/engineering-docker-images/issues/4456).

- `OVERLAYS` environment variable: This is a space separated list of overlay
  directories to run validation checks on.

  Default: If this is not set any directory containing standard Kustomize files
  in it will be used.
