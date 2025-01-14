# Copyright (c) 2025 Cisco and/or its affiliates.
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
        'parts': '''
You are a computer scientist, collaborating with the user,
wrapping your responses to line length of 80 (or fewer) characters.

The current content of IETF draft document is:
```markdown
${draft}
```
''',
    },
    {
        'role': 'user',
        'parts': '''
Reviewers pointed out there are multiple typos and stylistic errors.
Find one ocurence, write original sentence and corrected sentence,
and explain what you have changed and why.
''',
    },
    {
        'role': 'model',
        'parts': '''
Original:

> The bisection method, when unconditionally compliant with [RFC2544],
> is excessively slow.

Corrected:

> The bisection method, when used in a manner unconditionally compliant
> with [RFC2544], is excessively slow.

The phrase "when unconditionally compliant" is grammatically incorrect.  It
modifies "method" but compliance is a property of the *application* of the
method, not the method itself.  Rephrasing to "when used in a manner
unconditionally compliant with [RFC2544]" clarifies that it's the way the
bisection method is used, not the method itself, that determines compliance.
''',
    },
]
