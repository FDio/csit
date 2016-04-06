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

Documentation to files used to store URLs to resources in Honeycomb.
====================================================================

A URL file is a text file encoded in utf-8 with a path to a resource in
Honeycomb. There is only one line in each file.

The URL is stored without host and port with leading slash. There is no slash at
the end, e.g.:
    /restconf/config/v3po:vpp/bridge-domains
