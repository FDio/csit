# Copyright (c) 2023 Cisco and/or its affiliates.
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

import os
import string
import sys

template = string.Template(('''*** Test Cases ***
| ${name}
| | [Tags] | ${tags}
| | No Operation
'''))

def recurse(path, level):
    ospath = os.path.join(*path)
    os.mkdir(ospath)
    with open(f"{ospath}/__init__.robot", "w") as fout:
        pass
    tag_list = ["".join(path[:index + 1]) for index in range(len(path))]
    name = tag_list[-1]
    tag_string = " | ".join(tag_list)
    with open(f"{ospath}/s.robot", "w") as fout:
        fout.write(template.safe_substitute(dict(name=name, tags=tag_string)))
    tags = [name]
    if level > 0:
        ret = recurse(path + ["0"], level - 1)
        tags.extend(ret)
        ret = recurse(path + ["1"], level - 1)
        tags.extend(ret)
    return tags

level = int(sys.argv[1])
exprs = int(sys.argv[2])
tags = recurse(["t",], level)
print(f"{len(tags)} test cases generated", file=sys.stderr)
tags = [f"{tag}ANDt1*ANDt0*" for tag in tags[:exprs]]
includes = " ".join(f"--include {tag}" for tag in tags)
print(f"robot --dryrun --suite t {includes} t")
