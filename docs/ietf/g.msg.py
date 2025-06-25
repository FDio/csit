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
the newly renamed "Preview" subsection got one TODO (to get rewritten later),
and there is plenty of commentd from AD reviewer "Med"
that need addressing one way or the other.
I am Vratko (one of co-authors), focusing on content in this phase of editing,
while Maciek (the other coauthor) works on grammar and style in parallel
(so you can ignore typos for now).
Beofre I start making larger changes, I would like to improve
the section structure of the document.
(By chapters I mean the lines starting with `# `, plus abstract.
I call lines starting with `## ` sections and deeper parts subsections.)
I feel it has two many "scope" and "introduction" subsections,
each aiming at slightly different target
(industry situation; BMWG; this whole document; Specification; explanations).
Internal references need to be unambigous, so each subsection needs a different title,
making it hard to apply a systematic naming scheme without making titles long.

I know IETF documents tend to be classified as
"normative" (with requirements for implementing a standard)
and "informative" (with additional context and explanations
without being mandatory).
I feel the current draft has "normative parts" and "informative parts".
The main normative content is MLRsearch Specification,
together with directly related sections such as "requirements language"
Not sure if "terminology section" summarizing long definitions
is still a normative part, probably not as it does not add requirements.
Then we have "context" sections, both important ones that are readable
even before Specification, and less important ones describing quirks
that make sense when read after Specification.
Then we have clear "explanations" sections.
Some sections are not as clear to me with respect to this distinction.
For example the current "Overview" section of Specification chapter
relies too heavily on soon-to-be defined terms
to be considered as not directly related to normative parts.
I am thinking whether some of your 14 chapters can be demoted to sections
of new chapters, one "Context" before Specification,
one "Explanations" after Specification.

Here is the current high-level structure of the document
(most sections and all subsections omitted):
# Abstract
# Requirements Language
# Introduction
## Preview
## BMWG Documents
## Test Requirements
## MLRsearch position
# Identified Problems
## Long Search Duration
## DUT in SUT
## Repeatability and Comparability
## Throughput with Non-Zero Loss
## Inconsistent Trial Results
# MLRsearch Specification
## Scope
## Overview
## Quantities
## Existing Terms
## Trial Terms
## Goal Terms
## Auxiliary Terms
## Result Terms
## MLRsearch Architecture
## Compliance
# Further Explanations
# MLRsearch Logic and Example
# IANA Considerations
# Security Considerations
# Acknowledgements
# Appendix A: Load Classification
# Appendix B: Conditional Throughput
# Index

And here is what I currently think would be a better structure
(with comments in brackets):
# Abstract
# Requirements Language (despite the all-caps words should be concentrated only into MLR Specification chapter)
# Introduction (informative, not containing motivation yet)
## Preview (rename, rewrite, should explain the structure of following chapters and sections)
## BMWG Documents (informative)
## Test Requirements (informative but important)
## MLRsearch Position (informative as the context for Scope below)
# Identified Problems (informative but important for motivation)
## Long Search Duration
## DUT in SUT
## Repeatability and Comparability
## Throughput with Non-Zero Loss
## Inconsistent Trial Results
# MLRsearch Specification (main normative chapter)
## Scope (minimalistic but normative, as explained by MLRsearch Position above)
## Overview (informative, just to make next section more readable on first try)
## Terminology (new, to group similar subsections, all normative)
### Quantities
### Existing Terms
### Trial Terms
### Goal Terms
### Auxiliary Terms
### Result Terms
### MLRsearch Architecture
### Alphabetical list (former Index, strictly speaking not normative)
## Compliance (normative)
# Explanations (all informative again)
## (Renamed former Further Explanations)
## MLRsearch Logic and Example
# IANA Considerations
# Security Considerations
# Acknowledgements
# Appendix A: Load Classification
# Appendix B: Conditional Throughput

The new structure is not ideal, I may want to rename two informative chapters before Specification.
What do you think about this new proposed structure?
Do you see any improvements or other reasons to restructure
(to avoid forward references, for example) so the document is more readable in first pass?
(Med's comments show instances where he raised questions only to read the answer later.)
''',
    },
]
