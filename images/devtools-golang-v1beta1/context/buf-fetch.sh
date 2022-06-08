#!/usr/bin/env bash

script_dirname="$( dirname -- "${0}" )"

files=("buf-FILE_SELECTOR~buf" "protoc-gen-buf-breaking-FILE_SELECTOR~protoc-gen-buf-breaking" "protoc-gen-buf-lint-FILE_SELECTOR~protoc-gen-buf-breaking")

set -euo pipefail
set -x

: "${XDG_CACHE_HOME:="${HOME}/.cache"}"
: "${FILE_VERSION:=1.5.0}"

1>&2 declare -p FILE_VERSION XDG_CACHE_HOME

mkdir -vp "${XDG_CACHE_HOME}"

for file in "${files[@]}"
do
    ofile="${file##*~}"
    lfile="${file%%~*}"
    lfile="${lfile//FILE_SELECTOR/${FILE_SELECTOR}}"
    lfile="${lfile//FILE_VERSION/${FILE_VERSION}}"
    1>&2 declare -p ofile lfile
    wget -O "${XDG_CACHE_HOME}/${lfile}" "https://github.com/bufbuild/buf/releases/download/v${FILE_VERSION}/${lfile}"
    sed "/[\t ]${lfile}$/!d" "${script_dirname}/buf-${FILE_VERSION}.sha256sum" > "${XDG_CACHE_HOME}/${lfile}.sha256sum.tmp"
    (cd "${XDG_CACHE_HOME}" && sha256sum -c "${XDG_CACHE_HOME}/${lfile}.sha256sum.tmp")
    rm -v "${XDG_CACHE_HOME}/${lfile}.sha256sum.tmp"
    cp -v "${XDG_CACHE_HOME}/${lfile}" "${OUTPUT_PATH}/${ofile}"
    chmod +x "${OUTPUT_PATH}/${ofile}"
done
