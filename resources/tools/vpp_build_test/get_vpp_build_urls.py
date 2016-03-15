#!/usr/bin/python

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

"""This script creates file vpp_build_urls.txt with URL links to
the latest vpp build available on the nexus.fd.io server.
"""

import xml.etree.ElementTree as ET

# Path constants
base_url = 'https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp'
sub_dirs = ['vpp', 'vpp-dbg', 'vpp-dev', 'vpp-dpdk-dev', 'vpp-dpdk-dkms', 'vpp-lib']
vpp_versions_file = 'vpp_builds.xml'

# Get the string of the latest vpp build version
tree = ET.parse(vpp_versions_file)
root = tree.getroot()

date_list = []
dict = {}

for data in root.findall('data'):
    for content in data.findall('content-item'):
        text = content.find('text')
        date = content.find('lastModified')
        if 'maven-metadata' not in text.text:
            date_list.append(date.text)
            dict[date.text] = text.text

date_list.sort()
latest_build = dict[date_list[-1]]
print 'The latest version of VPP build to be downloaded: {}'.format(latest_build)

# Create URLs to VPP deb install packages. Delete vpp_build_urls.txt file if exits (option 'w' in open method)
with open('vpp_build_urls.txt', 'w') as vpp_paths:
    for dir in sub_dirs:
        path = '{0}/{1}/{2}/{1}-{2}.deb\n'.format(base_url, dir, latest_build)
        vpp_paths.write(path)
