#!/bin/bash
readonly SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
readonly UPSTREAM_DIR="${SCRIPT_DIR%/*}"
function main(){
    pre-commit run -c ${UPSTREAM_DIR}/common-pre-commit-config.yaml
}
main
