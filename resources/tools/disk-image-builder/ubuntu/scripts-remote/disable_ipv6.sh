#!/bin/sh -e

# Copyright (c) 2017 Cisco and/or its affiliates.
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


echo "********** Disabling IPv6 ***********"
# Disable on all existing interfaces
sysctl net.ipv6.conf.all.disable_ipv6=0
# Disable by default for any new interfaces
sysctl net.ipv6.conf.default.disable_ipv6=0