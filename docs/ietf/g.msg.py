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
Find one occurence, write original sentence and corrected sentence,
and explain what you have changed and why.
''',
    },
    {
        'role': 'model',
        'parts': '''
Original:

> Bridge learning frames are frames with source addresses that are the same as the destination addresses used by the test frames.

Corrected:

> Bridge learning frames are frames with source addresses equal to the destination addresses of the test frames.

Explanation:
Changed "that are the same as" to "equal to". While the original phrasing is grammatically correct, "equal to" is more concise and maintains the technical precision required in a specification document.  This aligns with the overall goal of clarity and conciseness in technical writing.
''',
    },
    {
        'role': 'user',
        'parts': '''
True, but that sentence is a quote from another document, so it should not be changed in this document. Pick another sentence.
''',
    },
    {
        'role': 'model',
        'parts': '''
Original:

> The primary reason for extending [RFC2544] is to address the challenges of evaluating and testing the data planes of software-based networking systems.

Corrected:

> The primary reason for extending [RFC2544] is to address the challenges of evaluating and testing the data plane of software-based networking systems.


Explanation:
Removed the unnecessary pluralization of "data planes".  A networking system generally has a single data plane, even if it consists of multiple devices.  The singular "data plane" is more accurate and commonly used in networking terminology.
''',
    },
    {
        'role': 'user',
        'parts': '''
I am not sure about that one, I will consult with my colleagues. In the meantime, pick another sentence.
''',
    },
]
