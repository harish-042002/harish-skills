#!/usr/bin/env bash
set -euo pipefail
aws cloudformation deploy --stack-name app --template-file template.yml
