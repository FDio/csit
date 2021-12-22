# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Utility to convert from .schema.yaml to .schema.json.

TODO: Read the input file name from command line argument.
"""

import glob
import json
import yaml


for filename in glob.glob(u"*.schema.yaml"):
    name = filename[:-5]
    with open(f"{name}.yaml", u"r") as fin, open(f"{name}.json", u"w") as fout:
        json.dump(yaml.load(fin.read()), fout, indent=2)
