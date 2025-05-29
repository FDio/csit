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
        'text': '''
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
        'text': '''
Reviewers gave us feedback on previous draft version.
The feedback was in a .doc document, not easily processable, so not visible in current draft content.
To address some of the feedback comments, I decided to add a "Scope" section.
Currently it only has few TODOs instead of proper outline.
Do you understand what I mean by those TODOs? If yes, write an outline of the future section.
''',
    },
    {
        'role': 'model',
        'text': '''
Here is an outline for the "Scope" section, interpreting your
TODOs and structuring them into what the document specifies and
what it does not:

# Scope

This section defines the scope of the MLRsearch methodology
specified in this document.

## What MLRsearch Specifies

*   **A Methodology for Throughput Search:** MLRsearch defines a
    methodology for determining data plane throughput, extending
    the throughput search procedure described in [RFC2544].
*   **Abstract System Components:** It specifies the roles and
    interactions of abstract components: the Manager, the
    Controller, and the Measurer.
*   **Key Definitions:** It provides precise definitions for
    search goals, trial parameters, and result metrics,
    including Load Classification and Conditional Throughput.
*   **Search Termination:** It covers both regular (successful)
    and irregular (e.g., aborted) search termination conditions
    and their corresponding results.
*   **Automation Focus:** MLRsearch is designed as a
    specification for automated benchmarking procedures,
    suitable for implementation as software libraries or tools.

## What MLRsearch Does Not Specify

*   **Other Benchmarking Tests:** This document focuses solely
    on throughput search. It does not specify methodologies for
    other benchmarking tests defined in [RFC2544], such as
    latency, back-to-back frames, or system recovery.
*   **Multiple Traffic Profiles:** A single MLRsearch execution
    is limited to one traffic profile (e.g., fixed frame size,
    specific traffic mix). It does not define how to search
    across multiple traffic profiles within a single run.
*   **Repeated Searches:** While MLRsearch aims to improve
    repeatability, this document specifies a single search
    execution. It does not define procedures for repeating
    searches for statistical analysis.
*   **Concrete Implementations:** MLRsearch defines abstract
    components and interfaces. It does not specify concrete
    APIs, programming languages, or specific hardware/software
    implementations.
*   **Controller Algorithms:** The document provides freedom for
    MLRsearch Implementations to choose specific algorithms for
    the Controller's load selection, aiming for optimal search
    duration.
*   **Detailed Test Setup:** Beyond the abstract components,
    this document does not prescribe specific test equipment,
    network topologies, or detailed SUT configurations.
''',
    },
]
