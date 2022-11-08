#!/bin/bash

IMAGE="cdash:latest"

docker build \
    --tag "${IMAGE}" \
    .

docker run \
    --rm \
    --name cdash_devcontainer \
    --user "$(id -u):$(id -g)"  \
    --volume "${HOME}/.aws:/.aws" \
    --volume "$(pwd)/app/:/app" \
    --volume "$(pwd)/../resources/libraries/python/jumpavg/:/app/cdash/jumpavg" \
    "${IMAGE}"