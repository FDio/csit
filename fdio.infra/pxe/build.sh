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
    --env "E_INT=$(ip -o -4 route show to default | awk '{print $5}')" \
    --env "E_ADD=$(hostname -I | awk '{print $1}')" \
    --cap-add NET_ADMIN \
    pxe-dnsmasq