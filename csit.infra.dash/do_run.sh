#!/usr/bin/env bash

set -exuo pipefail

command -v docker-compose || exit 1

#export UID=$(id -u)
#export GID=$(id -g)

docker-compose run \
    --user $(id -u):$(id -g) \
    --publish 5000 \
    --publish 9001 \
    dash
