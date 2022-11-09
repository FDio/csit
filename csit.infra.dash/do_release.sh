#!/usr/bin/env bash

set -exuo pipefail

command -v zip || exit 1

rm -f app.zip

pushd app
find . -type d -name "__pycache__" -exec rm -rf "{}" \; || true
find . -type d -name ".webassets-cache" -exec rm -rf "{}" \; || true
zip -r ../app.zip .
popd
