FROM ubuntu:20.04 as ubuntu_focal

LABEL Description="ubuntu intermediate image"
LABEL Version="2.0"

RUN apt update \
 && apt install -y wget genisoimage syslinux-common \
 && mkdir -p /var/lib/tftpboot/grub \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-focal-amd64/ \
 && mkdir -p /var/lib/tftpboot/casper/ubuntu-focal-arm64/

ENV ISO_FOCAL_AMD64 https://releases.ubuntu.com/20.04.2/ubuntu-20.04.2-live-server-amd64.iso
ENV ISO_FOCAL_ARM64 https://cdimage.ubuntu.com/releases/20.04/release/ubuntu-20.04.2-live-server-arm64.iso
ENV EFI_FOCAL_AMD64 http://archive.ubuntu.com/ubuntu/dists/focal/main/uefi/grub2-amd64/current/grubnetx64.efi.signed
ENV EFI_FOCAL_ARM64 http://ports.ubuntu.com/ubuntu-ports/dists/focal/main/uefi/grub2-arm64/current/grubnetaa64.efi.signed
ENV PXE_FOCAL_AMD64 http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/pxelinux.0
ENV LDL_FOCAL_AMD64 http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/ldlinux.c32

RUN echo "Preparing Grub EFI Binary" \
 && wget $EFI_FOCAL_AMD64 -O /var/lib/tftpboot/grub/grubnetx64.efi.signed \
 && wget $EFI_FOCAL_ARM64 -O /var/lib/tftpboot/grub/grubnetaa64.efi.signed

RUN echo "Preparing Grub LEGACY Binary" \
 && wget $EFI_FOCAL_AMD64 -O /var/lib/tftpboot/pxelinux.0 \
 && wget $LDL_FOCAL_AMD64 -O /var/lib/tftpboot/ldlinux.c32

RUN echo "Preparing casper kernel" \
 && wget $ISO_FOCAL_AMD64 -O /ubuntu-20.04.2-live-server-amd64.iso \
 && isoinfo -i /ubuntu-20.04.2-live-server-amd64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-focal-amd64/initrd \
 && isoinfo -i /ubuntu-20.04.2-live-server-amd64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-focal-amd64/vmlinuz\
 && wget $ISO_FOCAL_ARM64 -O /ubuntu-20.04.2-live-server-arm64.iso \
 && isoinfo -i /ubuntu-20.04.2-live-server-arm64.iso -x "/CASPER/INITRD.;1" > /var/lib/tftpboot/casper/ubuntu-focal-arm64/initrd \
 && isoinfo -i /ubuntu-20.04.2-live-server-arm64.iso -x "/CASPER/VMLINUZ.;1" > /var/lib/tftpboot/casper/ubuntu-focal-arm64/vmlinuz


FROM alpine

LABEL Description="dnsmasq service image"
LABEL Version="2.0"

RUN apk add --update --no-cache dnsmasq \
 && rm -rf /var/cache/apk/*

# Extract installer from previous image.
COPY --from=ubuntu_focal /var/lib/tftpboot /var/lib/tftpboot

# Configure PXE.
COPY tftpboot/ /var/lib/tftpboot/

# Configure DNSMASQ.
COPY etc/ /etc/

# Start dnsmasq. It picks up default configuration from /etc/dnsmasq.conf and
# /etc/default/dnsmasq plus any command line switch
ENTRYPOINT ["sh","-c","dnsmasq","--interface=$E_INT","--listen-address=$E_ADD"]
