#!/bin/bash
readonly SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
readonly UPSTREAM_DIR="${SCRIPT_DIR%/*}"
function main(){
    pre-commit run --all-files -c ${UPSTREAM_DIR}/.pre-commit-config.yaml
}
main
