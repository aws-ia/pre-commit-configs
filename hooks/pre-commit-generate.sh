#!/bin/bash
./utils/generate_ci_config.py \
    --cache-dir ~/.cache/pre-commit \
    --metadata-file-out configs/metadata.json \
    --config configs/pre-commit-ci-config.yaml \
    --input common-pre-commit-config.yaml \
    --output output/pre-commit-config-ci-generated.yaml
