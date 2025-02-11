#!/usr/bin/env bash

set -xuo pipefail

command -v docker || exit 1

export UID=$(id -u)
export GID=$(id -g)

docker network create csit-data || true
docker compose up --remove-orphans --detach
