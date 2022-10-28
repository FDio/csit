#!/bin/env bash

set -exuo pipefail

command -v zip || exit 1

rm -f app.zip

pushd app
zip -r ../app.zip .
popd
