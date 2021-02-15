FROM ubuntu:20.04 as ubuntu_focal

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget

ENV ISO_FOCAL_AMD64 https://releases.ubuntu.com/20.04.2/ubuntu-20.04.2-live-server-amd64.iso
ENV ISO_FOCAL_ARM64 https://cdimage.ubuntu.com/releases/20.04/release/ubuntu-20.04.2-live-server-arm64.iso

RUN echo "Preparing ISO Pre-cache" \
 && wget $ISO_FOCAL_AMD64 -O /ubuntu-20.04.2-live-server-amd64.iso \
 && wget $ISO_FOCAL_ARM64 -O /ubuntu-20.04.2-live-server-arm64.iso


FROM nginx:stable-alpine

LABEL Description="nginx service image"
LABEL Version="2.0"

ENV NGINX_FOCAL_AMD64 /usr/share/nginx/html/ubuntu_focal_amd64/
ENV NGINX_FOCAL_ARM64 /usr/share/nginx/html/ubuntu_focal_arm64/

RUN mkdir -p $NGINX_FOCAL_AMD64 \
 && mkdir -p $NGINX_FOCAL_ARM64

COPY --from=ubuntu_focal /ubuntu-20.04.2-live-server-amd64.iso $NGINX_FOCAL_AMD64/ubuntu-20.04.2-live-server-amd64.iso
COPY --from=ubuntu_focal /ubuntu-20.04.2-live-server-arm64.iso $NGINX_FOCAL_ARM64/ubuntu-20.04.2-live-server-arm64.iso

COPY html/ /usr/share/nginx/html/