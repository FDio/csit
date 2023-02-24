FROM ubuntu:22.04 as ubuntu_jammy

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget

ENV ISO_JAMMY_AMD64 https://old-releases.ubuntu.com/releases/22.04.1/ubuntu-22.04.1-live-server-amd64.iso
ENV ISO_JAMMY_ARM64 https://old-releases.ubuntu.com/releases/22.04.1/ubuntu-22.04.1-live-server-arm64.iso

RUN echo "Preparing ISO Pre-cache" \
 && wget $ISO_JAMMY_AMD64 -O /ubuntu-22.04.1-live-server-amd64.iso \
 && wget $ISO_JAMMY_ARM64 -O /ubuntu-22.04.1-live-server-arm64.iso


FROM nginx:stable-alpine

LABEL Description="nginx service image"
LABEL Version="2.0"

ENV NGINX_JAMMY_AMD64 /usr/share/nginx/html/ubuntu_jammy_amd64/
ENV NGINX_JAMMY_ARM64 /usr/share/nginx/html/ubuntu_jammy_arm64/

RUN mkdir -p $NGINX_JAMMY_AMD64 \
 && mkdir -p $NGINX_JAMMY_ARM64

COPY --from=ubuntu_jammy /ubuntu-22.04.1-live-server-amd64.iso $NGINX_JAMMY_AMD64/ubuntu-22.04.1-live-server-amd64.iso
COPY --from=ubuntu_jammy /ubuntu-22.04.1-live-server-arm64.iso $NGINX_JAMMY_ARM64/ubuntu-22.04.1-live-server-arm64.iso

COPY html/ /usr/share/nginx/html/