#!/bin/bash

# Clean.
docker container rm --force pxe-dnsmasq
docker image rm pxe-dnsmasq
docker container rm --force pxe-nginx
docker image rm pxe-nginx

# Build.
docker build \
    --network host \
    --build-arg HTTP_PROXY="$http_proxy" \
    --build-arg HTTPS_PROXY="$http_proxy" \
    --build-arg NO_PROXY="$no_proxy" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$http_proxy" \
    --build-arg no_proxy="$no_proxy" \
    --tag pxe-dnsmasq docker-dnsmasq/.

docker build \
    --build-arg HTTP_PROXY="$http_proxy" \
    --build-arg HTTPS_PROXY="$http_proxy" \
    --build-arg NO_PROXY="$no_proxy" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$http_proxy" \
    --build-arg no_proxy="$no_proxy" \
    --tag pxe-nginx docker-nginx/.

# Run.
docker run \
    --rm \
    --detach \
    --publish 8081:80 \
    --name pxe-nginx \
    pxe-nginx

docker run \
    --rm \
    --detach \
    --net host \
    --name pxe-dnsmasq \
    --env "E_INT=enp177s0np0" \
    --env "E_ADD=10.30.51.100" \
    --cap-add NET_ADMIN \
    pxe-dnsmasq