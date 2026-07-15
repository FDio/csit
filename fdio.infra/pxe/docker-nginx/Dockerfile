FROM ubuntu:26.04 AS ubuntu

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget

ENV ISO_NOBLE_AMD64=https://releases.ubuntu.com/releases/noble/ubuntu-24.04.4-live-server-amd64.iso
ENV ISO_NOBLE_ARM64=https://cdimage.ubuntu.com/releases/noble/release/ubuntu-24.04.4-live-server-arm64.iso
ENV ISO_RESOLUTE_AMD64=https://releases.ubuntu.com/releases/resolute/ubuntu-26.04-live-server-amd64.iso
ENV ISO_RESOLUTE_ARM64=https://cdimage.ubuntu.com/releases/resolute/release/ubuntu-26.04-live-server-arm64.iso

RUN echo "Preparing ISO Pre-cache" \
 && wget $ISO_NOBLE_AMD64 -O /ubuntu-24.04.4-live-server-amd64.iso \
 && wget $ISO_NOBLE_ARM64 -O /ubuntu-24.04.4-live-server-arm64.iso \
 && wget $ISO_RESOLUTE_AMD64 -O /ubuntu-26.04-live-server-amd64.iso \
 && wget $ISO_RESOLUTE_ARM64 -O /ubuntu-26.04-live-server-arm64.iso


FROM nginx:stable-alpine

LABEL Description="nginx service image"
LABEL Version="2.0"

ENV NGINX_NOBLE_AMD64=/usr/share/nginx/html/ubuntu_noble_amd64/
ENV NGINX_NOBLE_ARM64=/usr/share/nginx/html/ubuntu_noble_arm64/
ENV NGINX_RESOLUTE_AMD64=/usr/share/nginx/html/ubuntu_resolute_amd64/
ENV NGINX_RESOLUTE_ARM64=/usr/share/nginx/html/ubuntu_resolute_arm64/

RUN mkdir -p $NGINX_NOBLE_AMD64 \
 && mkdir -p $NGINX_NOBLE_ARM64 \
 && mkdir -p $NGINX_RESOLUTE_AMD64 \
 && mkdir -p $NGINX_RESOLUTE_ARM64

COPY --from=ubuntu /ubuntu-24.04.4-live-server-amd64.iso $NGINX_NOBLE_AMD64/ubuntu-24.04.4-live-server-amd64.iso
COPY --from=ubuntu /ubuntu-24.04.4-live-server-arm64.iso $NGINX_NOBLE_ARM64/ubuntu-24.04.4-live-server-arm64.iso
COPY --from=ubuntu /ubuntu-26.04-live-server-amd64.iso $NGINX_RESOLUTE_AMD64/ubuntu-26.04-live-server-amd64.iso
COPY --from=ubuntu /ubuntu-26.04-live-server-arm64.iso $NGINX_RESOLUTE_ARM64/ubuntu-26.04-live-server-arm64.iso

COPY html/ /usr/share/nginx/html/
