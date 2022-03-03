# AWS-IA opinioniated pre-commit hooks

This repo serves as a centralized place to define pre-commit hooks in-use across AWS-IA repositories. The primary mission of this project is to serve the needs of repositories with-in this org.

Specific toolsets are *_opinioniated_* and we recognize that alternatives may be available. 


## Installation

`.pre-commit-config.yaml`

```
---
fail_fast: false
minimum_pre_commit_version: "2.6.0"
repos:
  -
    repo: https://github.com/aws-ia/pre-commit-hooks
    rev: v1.0
    hooks:
      - id: aws-ia-meta-hook
```