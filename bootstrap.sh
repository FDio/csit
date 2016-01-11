#!/bin/bash
set -euf -o pipefail

git clone ssh://rotterdam-jobbuilder@gerrit.fd.io:29418/vpp

cd vpp/build-root
./bootstrap.sh
make PLATFORM=vpp TAG=vpp_debug install-deb

ls -la
