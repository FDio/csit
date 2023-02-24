FROM ubuntu:22.04 as ubuntu_jammy

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget genisoimage syslinux-common \
 && mkdir -p /var/lib/tftpboot/grub \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-jammy-amd64/ \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-jammy-arm64/

ENV ISO_JAMMY_AMD64 https://old-releases.ubuntu.com/releases/22.04.1/ubuntu-22.04.1-live-server-amd64.iso
ENV ISO_JAMMY_ARM64 https://old-releases.ubuntu.com/releases/22.04.1/ubuntu-22.04.1-live-server-arm64.iso
ENV EFI_JAMMY_AMD64 http://archive.ubuntu.com/ubuntu/dists/jammy/main/uefi/grub2-amd64/current/grubnetx64.efi.signed
ENV EFI_JAMMY_ARM64 http://ports.ubuntu.com/ubuntu-ports/dists/jammy/main/uefi/grub2-arm64/current/grubnetaa64.efi.signed

RUN echo "Preparing Grub EFI Binary" \
 && wget $EFI_JAMMY_AMD64 -O /var/lib/tftpboot/grub/grubnetx64.efi.signed \
 && wget $EFI_JAMMY_ARM64 -O /var/lib/tftpboot/grub/grubnetaa64.efi.signed

RUN echo "Preparing Casper Kernel" \
 && wget $ISO_JAMMY_AMD64 -O /ubuntu-22.04.1-live-server-amd64.iso \
 && isoinfo -i /ubuntu-22.04.1-live-server-amd64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-jammy-amd64/initrd \
 && isoinfo -i /ubuntu-22.04.1-live-server-amd64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-jammy-amd64/vmlinuz\
 && wget $ISO_JAMMY_ARM64 -O /ubuntu-22.04.1-live-server-arm64.iso \
 && isoinfo -i /ubuntu-22.04.1-live-server-arm64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-jammy-arm64/initrd \
 && isoinfo -i /ubuntu-22.04.1-live-server-arm64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-jammy-arm64/vmlinuz

FROM alpine

LABEL Description="dnsmasq service image"
LABEL Version="2.0"

RUN apk add --update --no-cache dnsmasq \
 && rm -rf /var/cache/apk/*

# Extract installer from previous image.
COPY --from=ubuntu_jammy /var/lib/tftpboot /var/lib/tftpboot

# Configure PXE.
COPY tftpboot/ /var/lib/tftpboot/

# Configure DNSMASQ.
COPY etc/ /etc/

# Start dnsmasq. It picks up default configuration from /etc/dnsmasq.conf and
# /etc/default/dnsmasq plus any command line switch
ENTRYPOINT ["sh","-c","dnsmasq","--interface=$E_INT","--listen-address=$E_ADD"]