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
    "memory_size": 100,
    "skip_n_vectors": 1,
    "match_n_vectors": 1,
    "miss_next_index": 1,
    "mask": "00:00:00:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
}

hc_acl_table2 = {
    "name": "acl_table_test2",
    "nbuckets": 1,
    "memory_size": 100,
    "skip_n_vectors": 1,
    "match_n_vectors": 1,
    "next_table": "acl_table_test",
    "miss_next_index": 1,
    "mask": "ff:ff:ff:00:00:00:ff:ff:ff:ff:ff:ff:00:00:00:00"
}
# representation of table settings in VAT
table_index = 0
vat_acl_table = {
    "nbuckets": hc_acl_table['nbuckets'],
    "skip": hc_acl_table['skip_n_vectors'],
    "match": hc_acl_table['match_n_vectors'],
    "nextnode": hc_acl_table['miss_next_index'],
    "nexttbl": -1,
    "mask": hc_acl_table['mask'].replace(":", ""),
    "sessions": 0
}
table_index2 = 1
vat_acl_table2 = {
    "nbuckets": hc_acl_table2['nbuckets'],
    "skip": hc_acl_table2['skip_n_vectors'],
    "match": hc_acl_table2['match_n_vectors'],
    "nextnode": hc_acl_table2['miss_next_index'],
    "nexttbl": table_index,
    "mask": hc_acl_table2['mask'].replace(":", ""),
    "sessions": 0
}
# setting for acl sessions
hc_acl_session = {
    "match": "00:00:00:00:00:00:01:02:03:04:05:06:00:00:00:00",
    "hit_next_index": 1,
    "opaque_index": 1,
    "advance": 1
}

hc_acl_session2 = {
    "match": "00:00:00:00:00:00:06:05:04:03:02:01:00:00:00:00",
    "hit_next_index": 1,
    "opaque_index": 1,
    "advance": 1
}
# representation of session settings in VAT
session_index = 0
vat_acl_session = {
    "match": hc_acl_session['match'].replace(":", ""),
    "advance": hc_acl_session['advance'],
    "opaque": hc_acl_session['opaque_index'],
    "next_index": hc_acl_session['hit_next_index']
}
session_index2 = 1
vat_acl_session2 = {
    "index": 1,
    "match": hc_acl_session2['match'].replace(":", ""),
    "advance": hc_acl_session2['advance'],
    "opaque": hc_acl_session2['opaque_index'],
    "next_index": hc_acl_session2['hit_next_index']
}
