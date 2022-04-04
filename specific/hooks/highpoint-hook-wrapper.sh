#!/bin/bash
readonly SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
readonly UPSTREAM_DIR="${SCRIPT_DIR%/*}"
readonly METADATA_DIR=".metadata"
function main() {
  if [ -d "$METADATA_DIR" ] 
  then
    for cfg in $METADATA_DIR/*; do
        PROJECT_TYPE=$(basename ${cfg})
        echo "Running: Pre${cfg}"
        pre-commit run -a -c $UPSTREAM_DIR/.pre-commit-config-${PROJECT_TYPE}.yaml
      done
  else
    echo "Error: project metadata not found"
    exit 1
  fi
}
main
