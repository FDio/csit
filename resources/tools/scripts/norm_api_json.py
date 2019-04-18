# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Script to sort contents of .api.json files within a tree.

Most of implementation is copypasted from:
https://github.com/opendaylight/integration-test/blob/8d9fde3e0d522eb4714fbbee642054560143b948/csit/libraries/norm_json.py

TODO: Publish the library in PyPI.
"""

import collections as _collections
try:
    import simplejson as _json
except ImportError:  # Python2.7 calls it json.
    import json as _json


class _Hsfl(list):
    """
    Hashable sorted frozen list implementation stub.

    Supports only __init__, __repr__ and __hash__ methods.
    Other list methods are available, but they may break contract.
    """

    def __init__(self, *args, **kwargs):
        """Contruct super, sort and compute repr and hash cache values."""
        sup = super(_Hsfl, self)
        sup.__init__(*args, **kwargs)
        sup.sort(key=repr)
        self.__repr = repr(tuple(self))
        self.__hash = hash(self.__repr)

    def __repr__(self):
        """Return cached repr string."""
        return self.__repr

    def __hash__(self):
        """Return cached hash."""
        return self.__hash


class _Hsfod(_collections.OrderedDict):
    """
    Hashable sorted (by key) frozen OrderedDict implementation stub.

    Supports only __init__, __repr__ and __hash__ methods.
    Other OrderedDict methods are available, but they may break contract.
    """

    def __init__(self, *args, **kwargs):
        """Put arguments to OrderedDict, sort, pass to super, cache values."""
        self_unsorted = _collections.OrderedDict(*args, **kwargs)
        items_sorted = sorted(self_unsorted.items(), key=repr)
        sup = super(_Hsfod, self)  # Possibly something else than OrderedDict.
        sup.__init__(items_sorted)
        # Repr string is used for sorting, keys are more important than values.
        self.__repr = "".join([
            "{", repr(self.keys()), ":", repr(self.values()), "}"])
        self.__hash = hash(self.__repr)

    def __repr__(self):
        """Return cached repr string."""
        return self.__repr

    def __hash__(self):
        """Return cached hash."""
        return self.__hash


def _hsfl_array(s_and_end, scan_once, **kwargs):
    """Scan JSON array as usual, but return hsfl instead of list."""
    values, end = _json.decoder.JSONArray(s_and_end, scan_once, **kwargs)
    return _Hsfl(values), end


class _Decoder(_json.JSONDecoder):
    """Private class to act as customized JSON decoder.

    Based on: http://stackoverflow.com/questions/10885238/
    python-change-list-type-for-json-decoding
    """

    def __init__(self, **kwargs):
        """Initialize decoder with special array implementation."""
        _json.JSONDecoder.__init__(self, **kwargs)
        # Use the custom JSONArray
        self.parse_array = _hsfl_array
        # Use the python implemenation of the scanner
        self.scan_once = _json.scanner.py_make_scanner(self)


def loads_sorted(text, strict=False):
    """Return Python object with sorted arrays and dictionary keys."""
    object_decoded = _json.loads(text, cls=_Decoder, object_hook=_Hsfod)
    return object_decoded


def dumps_indented(obj, indent=1):
    """Wrapper for json.dumps with default indentation level. Adds newline."""
    pretty_json = _json.dumps(obj, separators=(",", ": "), indent=indent)
    return pretty_json + '\n'  # To avoid diff "no newline" warning line.


def normalize_json_text(text, strict=False, indent=1):
    """
    Attempt to return sorted indented JSON string.

    If parse error happens:
    If strict is true, raise the exception.
    If strict is not true, return original text with error message.
    """
    try:
        object_decoded = loads_sorted(text)
    except ValueError as err:
        if strict:
            raise err
        else:
            return "".join([str(err), "\n", text])
    pretty_json = dumps_indented(object_decoded, indent=indent)
    return pretty_json


import os
import sys

if len(sys.argv) != 2:
    print "Usage: {} PATH_TO_TREE_ROOT".format(sys.argv[0])
    print "This will rewrite the contents of recursively found"
    print ".api.json files with the same but sorted json content."
    sys.exit(1)
for root, subdirs, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        if not filename.endswith(".api.json"):
            continue
        pathname = "".join([root, "/", filename])
        with open(pathname, "r") as file_in:
            text_in = file_in.read()
        text_out = normalize_json_text(text_in)
        with open(pathname, "w") as file_out:
            file_out.write(text_out)
