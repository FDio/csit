# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""Utility to validate a json schema against its metaschema.

TODO: Read the input file name from command line argument.
TODO: Make callable from another working directory.
"""

import glob
import json
import jsonschema


for filename in glob.glob(u"*.schema.json"):
    with open(filename, u"rt", encoding="utf-8") as file_in:
        schema = json.load(file_in)
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)

print(u"Schemas are valid.")
