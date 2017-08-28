#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

####set -x
CSIT_INSTALL_DIR=`pwd`/../../..
CSIT_TEMP_DIR="/tmp/openvpp-testing"

rm $CSIT_TEMP_DIR
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/configs/system-config.yaml
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/configs/*~
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/dryrun/etc/default/*
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/dryrun/etc/sysctl.d/*
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/dryrun/etc/vpp/startup.conf
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/dryrun/etc/vpp/*.orig
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/dryrun/etc/vpp/*~
rm $CSIT_INSTALL_DIR/resources/tools/auto-config/scripts/*~

unset PYTHONPATH
cd $CSIT_INSTALL_DIR/..
find csit/resources/tools/auto-config/.
echo "PYTHONPATH: $PYTHONPATH"
####set +x


