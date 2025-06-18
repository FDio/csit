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
## Requirements Language (as not used outside the normative Specification chapter)
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

The new structure is not ideal, I may want to rename first two informative chapters.
What do you think about this new proposed structure?
Do you see any improvements or other reasons to restrusture
(to avoid forward references, for example) so the document is more readable in first pass?
(Med's comments show instances where he raised questions only to read answer later.)
''',
    },
    {
        'role': 'model',
        'text': '''
Vratko, this is a solid direction for restructuring the draft.
Separating normative and informative content, and
consolidating terminology, will significantly improve
readability and address the forward reference issue.

Here's my feedback on your proposed structure,
followed by a refined suggestion:

Your proposed structure:

*   **Abstract**
*   **Introduction** (informative, not containing motivation yet)
    *   Preview
    *   BMWG Documents
    *   Test Requirements
    *   MLRsearch Position
*   **Identified Problems** (informative but important for motivation)
    *   ... (motivation)
*   **MLRsearch Specification** (main normative chapter)
    *   Requirements Language
    *   Scope
    *   Overview
    *   Terminology (new, to group similar subsections, all normative)
        *   Quantities
        *   Existing Terms
        *   Trial Terms
        *   Goal Terms
        *   Auxiliary Terms
        *   Result Terms
        *   MLRsearch Architecture
        *   Alphabetical list (former Index, strictly speaking not normative)
    *   Compliance
*   **Explanations** (all informative again)
    *   (Renamed former Further Explanations)
    *   MLRsearch Logic and Example
*   **IANA Considerations**
*   **Security Considerations**
*   **Acknowledgements**
*   **Appendix A: Load Classification**
*   **Appendix B: Conditional Throughput**

**Feedback on your proposal:**

1.  **`Requirements Language` Placement:**
    *   You propose moving it *inside* `MLRsearch Specification`.
    *   **Recommendation:** Keep `Requirements Language` as a top-level
        chapter, immediately after `Abstract`. The BCP 14 keywords
        ("MUST", "SHOULD", etc.) apply to the *entire* document, not
        just the specification chapter. Placing it early clarifies
        its global applicability.

2.  **`Introduction` Chapter:**
    *   The content (`Preview`, `BMWG Documents`, `Test Requirements`,
        `MLRsearch Position`) fits well as an informative setup.
    *   **Suggestion:** Consider renaming `Preview` to something like
        `Document Structure` or `About This Document` to clearly
        signal its purpose of guiding the reader through the draft.

3.  **`Identified Problems` Chapter:**
    *   This is clearly informative and provides the essential
        motivation. Keeping it as a top-level chapter is appropriate.
    *   **Suggestion:** `Problem Statement` is a common, formal
        alternative title, but `Identified Problems` is also clear.

4.  **`MLRsearch Specification` Chapter:**
    *   This is the core normative part, excellent.
    *   **`Scope`:** Good to keep it minimalistic and normative here.
    *   **`Overview`:** This is tricky. An overview should give a
        high-level picture. If it relies on terms defined later, it
        can be confusing.
        *   **Suggestion:** Make this `Overview` truly high-level.
            Introduce the *components* (`Manager`, `Controller`,
            `Measurer`) and their *roles* and *interactions* here,
            but defer the detailed definitions of their inputs/outputs
            (e.g., `Trial Input`, `Search Goal`) to the `Terminology`
            section. This reduces forward references.
    *   **`Terminology` (New Section):** This is the most significant
        and beneficial change. Grouping all definitions here is
        excellent for readability and avoiding forward references.
        *   **Normative Status:** The *definitions themselves* are
            normative. The `Alphabetical list` (Index) is informative.
            You can state this explicitly within the `Terminology`
            section.
        *   **`MLRsearch Architecture` within Terminology:** Yes,
            defining the components (`Manager`, `Controller`, `Measurer`)
            as terms within `Terminology` is a good fit.
    *   **`Compliance`:** Good placement, as it defines how to adhere
        to the specification.

5.  **`Explanations` Chapter:**
    *   Grouping `Further Explanations` and `MLRsearch Logic and Example`
        here is logical and clearly separates the "how-to" and "why"
        from the "what" (specification).
    *   **Suggestion:** Rename `(Renamed former Further Explanations)`
        to something more descriptive, like `Core Concepts Explained`
        or `Detailed Discussion`.

6.  **Appendices:**
    *   Keeping `Load Classification` and `Conditional Throughput` as
        appendices is standard and appropriate, as they contain the
        formal algorithms referenced from the `Explanations` chapter.

**Refined Proposed Structure:**

```
# Abstract
# Requirements Language (Applies to the entire document)

# Introduction (Informative: Sets the stage for the document)
## About This Document (Explains document structure, normative/informative parts)
## BMWG Context (Role of BMWG, general test requirements)
## MLRsearch Position (How this document fits within BMWG recommendations)

# Problem Statement (Informative: Motivation for MLRsearch)
## Long Search Duration
## DUT in SUT
## Repeatability and Comparability
## Throughput with Non-Zero Loss
## Inconsistent Trial Results

# MLRsearch Specification (Normative: The core standard)
## Scope (What this specification covers)
## Overview (High-level components: Manager, Controller, Measurer, their interaction)
## Terminology (Normative definitions of all terms used in the specification)
### SUT, DUT, Trial (Existing terms, re-defined/clarified)
### Trial Terms (Input, Output, Duration, Load, Ratios)
### Goal Terms (Search Goal and its attributes)
### Auxiliary Terms (Trial Classification, Load Classification)
### Result Terms (Goal Result, Search Result, Relevant Bounds, Conditional Throughput)
### Architecture Components (Manager, Controller, Measurer - formal definitions)
## Compliance (How to comply with MLRsearch, specific MLRsearch instances)

# Explanations (Informative: Deeper dive into concepts, logic, examples)
## Core Concepts Explained (Discussion of binary search, stopping conditions, precision)
## Loss Ratios and Inversion (Detailed explanation of these concepts)
## Exceed Ratio and Multiple Trials
## Short Trials and Duration Selection
## Generalized Throughput (Hard limits, variability)
## MLRsearch Logic (High-level explanation of algorithms, referring to appendices)
## Example Search (Detailed walkthrough)

# IANA Considerations
# Security Considerations
# Acknowledgements

# Appendix A: Load Classification (Formal algorithm)
# Appendix B: Conditional Throughput (Formal algorithm)
# Index (Alphabetical list of terms, informative)
```

This structure maintains your excellent idea of separating normative
and informative content, consolidates terminology, and addresses the
placement of `Requirements Language` for global applicability. It
should significantly improve the document's flow and reduce the need
for forward references.
''',
    },
]
