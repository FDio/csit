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
As you can see, the current document is in the middle of a rewrite.
The "Scope" section consisting entirely of TODOs,
the newly renamed "Preview" subsection got one TODO,
and there is plenty of commentd from AD reviewer "Med"
that need addressing one way or the other.
I am Vratko (one of co-authors), focusing on content in this phase of editing,
while Maciek (the other coauthor) works on grammar and style in parallel
(so you can ignore typos for now).
Beofre I start making larger changes, I would like to improve the sectionstructure of the document.
I feel it has two many "scope" and "introduction" subsections,
each aiming at slightly different target (industry situation; BMWG; this whole document; Specification; explanations).
Internal references need to be unambigous, so each subsection needs a different title,
making it hard to apply a systematic naming scheme without making titles long.

So my first question to you is what would be the chapters in future ideally-edited documents?
By chapters I mean the lines starting with `# `, plus abstract.
I call lines starting with `## ` sections and deeper parts subsections.
Propose a list of chapters, including their titles and high-level description of their content.
''',
    },
    {
        'role': 'model',
        'text': '''
Okay, Vratko, let's think about a clearer chapter structure.
The current document mixes introduction, problem
description, specification details, and explanations
across several top-level sections.

Here is a proposed structure focusing on a logical flow:

1.  **Abstract**: Standard summary of the document's purpose
    and key contributions.

2.  **Introduction**: Set the stage. Explain the context
    (BMWG, benchmarking goals), state the document's
    purpose (proposing MLRsearch), and briefly mention
    the problems it addresses. This would absorb parts
    of the current "Introduction" and "Preview".

3.  **Requirements Language**: Standard section defining
    the use of normative keywords (MUST, SHOULD, etc.).
    Placed after the main introduction.

4.  **Terminology**: Define all key terms used in the
    document. This includes terms from RFCs (like SUT,
    DUT, Trial) and new terms introduced by MLRsearch
    (like Search Goal, Load Classification, Conditional
    Throughput). This centralizes definitions.

5.  **Problem Statement**: Detail the specific challenges
    with existing benchmarking methodologies, particularly
    for modern systems, that MLRsearch is designed to
    overcome. This corresponds to the current
    "Identified Problems" chapter.

6.  **MLRsearch Overview**: Provide a high-level description
    of the MLRsearch methodology. Introduce the core
    concepts, the abstract components (Manager, Controller,
    Measurer), and how they interact. This would cover
    the conceptual parts of the current "Overview" and
    "MLRsearch Architecture".

7.  **MLRsearch Specification**: This is the core normative
    chapter. It formally defines all the quantities
    (Trial, Goal, Result terms) and the requirements
    for a compliant implementation. This would contain
    the precise definitions currently under "MLRsearch
    Specification", potentially split into subsections
    like "Quantities" and "Architecture Requirements".

8.  **MLRsearch Logic**: Explain the key algorithms
    (Load Classification, Conditional Throughput) conceptually.
    Describe *what* they do and *why*, referencing the
    appendices for the formal *how* (pseudocode). This
    would cover the conceptual parts of the current
    "MLRsearch Logic and Example".

9.  **Compliance and Relation to Other Benchmarks**: Explain
    how MLRsearch relates to RFC 2544, TST 009, and other
    benchmarking procedures. Detail how compliance is
    determined and how MLRsearch can be used to achieve
    results compatible with other standards. This corresponds
    to the current "Compliance" section.

10. **Operational Considerations and Discussion**: Discuss
    practical aspects, SUT behavior models (noise, variability),
    the impact of configuration options (like Goal Exceed
    Ratio, Short Trials), trade-offs (duration vs. precision),
    and further insights into the methodology. This would
    absorb content from "Further Explanations" and parts
    of "MLRsearch Logic and Example" related to SUT behavior.

11. **Example Search**: A detailed walk-through of a
    hypothetical MLRsearch run to illustrate the concepts,
    logic, and how results are derived. This could also
    potentially be an appendix if preferred.

12. **IANA Considerations**: Standard section.

13. **Security Considerations**: Standard section.

14. **Appendices**: Contains formal pseudocode for the
    algorithms (Load Classification, Conditional Throughput)
    and the Index.

This structure separates the "why" (Introduction, Problems)
from the "what" (Overview, Specification) and the "how"
(Logic, Appendices), while also providing practical
discussion and examples. It centralizes definitions and
compliance information.
''',
    },
]
