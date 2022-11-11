#!/usr/bin/env bash

set -xuo pipefail

command -v zip || exit 1

rm -f app.zip

pushd app
find . -type d -name "__pycache__" -exec rm -rf "{}" \;
find . -type d -name ".webassets-cache" -exec rm -rf "{}" \;
zip -r ../app.zip .
popd
