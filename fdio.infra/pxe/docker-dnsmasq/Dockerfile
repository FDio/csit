FROM ubuntu:24.04 AS ubuntu_noble

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget genisoimage syslinux-common \
 && mkdir -p /var/lib/tftpboot/grub \
 && mkdir -p /var/lib/tftpboot/grub/fonts \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-noble-amd64/ \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-noble-arm64/

ENV ISO_NOBLE_AMD64 https://releases.ubuntu.com/releases/noble/ubuntu-24.04-live-server-amd64.iso
ENV ISO_NOBLE_ARM64 https://cdimage.ubuntu.com/releases/noble/release/ubuntu-24.04-live-server-arm64.iso
ENV EFI_NOBLE_AMD64 http://archive.ubuntu.com/ubuntu/dists/jammy/main/uefi/grub2-amd64/current/grubnetx64.efi.signed
ENV EFI_NOBLE_ARM64 http://ports.ubuntu.com/ubuntu-ports/dists/jammy/main/uefi/grub2-arm64/current/grubnetaa64.efi.signed

RUN echo "Preparing Grub EFI Binary" \
 && wget $EFI_NOBLE_AMD64 -O /var/lib/tftpboot/grubx64.efi \
 && wget $EFI_NOBLE_ARM64 -O /var/lib/tftpboot/grubaa64.efi \
 && apt download shim-signed \
 && dpkg-deb --fsys-tarfile shim-signed*deb | tar x ./usr/lib/shim/shimx64.efi.signed.latest -O > /var/lib/tftpboot/bootx64.efi \
 && apt download grub-common \
 && dpkg-deb --fsys-tarfile grub-common*deb | tar x ./usr/share/grub/unicode.pf2 -O > /var/lib/tftpboot/grub/fonts/unicode.pf2

RUN echo "Preparing Casper Kernel" \
 && wget $ISO_NOBLE_AMD64 -O /ubuntu-24.04-live-server-amd64.iso \
 && isoinfo -i /ubuntu-24.04-live-server-amd64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-noble-amd64/initrd \
 && isoinfo -i /ubuntu-24.04-live-server-amd64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-noble-amd64/vmlinuz \
 && wget $ISO_NOBLE_ARM64 -O /ubuntu-24.04-live-server-arm64.iso \
 && isoinfo -i /ubuntu-24.04-live-server-arm64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-noble-arm64/initrd \
 && isoinfo -i /ubuntu-24.04-live-server-arm64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-noble-arm64/vmlinuz

FROM alpine

LABEL Description="dnsmasq service image"
LABEL Version="2.0"

RUN apk add --update --no-cache dnsmasq \
 && rm -rf /var/cache/apk/*

# Extract installer from previous image.
COPY --from=ubuntu_noble /var/lib/tftpboot /var/lib/tftpboot

# Configure PXE.
COPY tftpboot/ /var/lib/tftpboot/

# Configure DNSMASQ.
COPY etc/ /etc/

# Start dnsmasq. It picks up default configuration from /etc/dnsmasq.conf and
# /etc/default/dnsmasq plus any command line switch
ENTRYPOINT ["sh","-c","dnsmasq","--interface=$E_INT","--listen-address=$E_ADD"]
