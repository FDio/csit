# Copyright (c) 2024 Cisco and/or its affiliates.
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

messages = [
    {
        'role': 'system',
        'content': '''
You are a computer scientist, collaborating with the user.
The current content of IETF draft document is:
```
${draft}
```
''',
    },
    {
        'role': 'user',
        'content': '''
Pick one sentence that is wrong, explain what is wrong,
write an improved version of it, and tell me what have you changed.
''',
    },
]
