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

"""Test variables for access control list test suite."""

# settings for acl tables
hc_acl_table = {
    "name": "acl_table_test",
    "nbuckets": 1,
    "memory_size": 100000,
    "skip_n_vectors": 1,
    "miss_next": "permit",
    "mask": "00:00:00:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
}

hc_acl_table2 = {
    "name": "acl_table_test2",
    "nbuckets": 2,
    "memory_size": 100000,
    "skip_n_vectors": 1,
    "next_table": "acl_table_test",
    "miss_next": "deny",
    "mask": "ff:ff:ff:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
}
# representation of table settings in VAT
table_index = 0
vat_acl_table = {
    "nbuckets": hc_acl_table['nbuckets'],
    "skip": 0,
    "match": 1,
    "nextnode": -1,
    "nexttbl": -1,
    "mask": hc_acl_table['mask'].replace(":", ""),
}
table_index2 = 1
vat_acl_table2 = {
    "nbuckets": hc_acl_table2['nbuckets'],
    "skip": 1,
    "match": 1,
    "nextnode": 0,
    "nexttbl": table_index,
    "mask": hc_acl_table2['mask'].replace(":", ""),
}
# setting for acl sessions
hc_acl_session = {
    "match": "00:00:00:00:00:00:01:02:03:04:05:06:00:00:00:00",
    "hit_next": "permit",
    "opaque_index": 1,
    "advance": 1
}

hc_acl_session2 = {
    "match": "00:00:00:00:00:00:06:05:04:03:02:01:00:00:00:00",
    "hit_next": "deny",
    "opaque_index": 1,
    "advance": 1
}
# representation of session settings in VAT
session_index = 0
vat_acl_session = {
    "match": hc_acl_session['match'].replace(":", ""),
    "advance": hc_acl_session['advance'],
    "opaque": hc_acl_session['opaque_index'],
    "next_index": -1
}
session_index2 = 1
vat_acl_session2 = {
    "match": hc_acl_session2['match'].replace(":", ""),
    "advance": hc_acl_session2['advance'],
    "opaque": hc_acl_session2['opaque_index'],
    "next_index": session_index
}
