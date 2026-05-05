# Contributing to this Project

First off, thank you for considering contributing! We value all contributions, whether they are bug fixes, new features, documentation updates, or architectural improvements. 

To ensure the legal integrity of this project and protect both our contributors and downstream users, we have established guidelines for licensing, provenance tracking, and the use of Generative AI.

## 1. Licensing Overview

This project uses a dual-licensing model depending on the type of contribution:
* **Code Contributions:** Licensed under the **Apache License 2.0**.
* **Documentation Contributions:** Licensed under the **Creative Commons Attribution 4.0 International License (CC-BY-4.0)**.

We track licensing at the file level using [SPDX License Identifiers](https://spdx.dev/ids/). Files containing human-authored, copyrightable material must include the appropriate SPDX header at the top of the file (e.g., `SPDX-License-Identifier: Apache-2.0`).

## 2. Developer Certificate of Origin (DCO)

We require all contributions to comply with the Developer Certificate of Origin (DCO) version 1.1. We do not use Contributor License Agreements (CLAs). 

To certify your compliance, every commit must include a `Signed-off-by` line in the commit message. 

**Requirements for Signed-off-by:**
* The signing entity **must be a human person**. AI agents, bots, and automated tools cannot legally certify the DCO.
* You must use a valid personal or corporate e-mail address. Group aliases or mailing lists are not permitted.
* By adding this line, you are taking full legal responsibility for the contribution and affirming that you have the right to submit it under the project's licenses.

Example:
`Signed-off-by: Jane Doe <jane.doe@example.com>`

## 3. Commit Taxonomy and Provenance Tracking

With the rise of Generative AI and the inclusion of Public Domain code (such as work by US Federal Government employees), tracking the provenance of our codebase is critical. 

While our release snapshots are governed at the file level by SPDX identifiers, our Git history acts as a granular provenance database. Every commit must fall into one of the following four categories:

### Type 1: Copyrightable Human Additions
* **Definition:** Wholly original human-authored code/documentation, or substantive, creative human edits to previously copyrighted parts of the codebase.
* **Action:** The file must contain the appropriate SPDX License Identifier (`Apache-2.0` or `CC-BY-4.0`).
* **Commit Message:** Standard `Signed-off-by` required.

### Type 2: Uncopyrightable / Public Domain Additions
* **Definition:** Purely AI-generated code/documentation with no substantive human modification, or newly introduced Public Domain code.
* **Action:** If this creates a new file, do not add an Apache-2.0 or CC-BY-4.0 SPDX identifier, as the file lacks human authorship.
* **Commit Message:** Requires `Signed-off-by` (the human takes responsibility) **AND** an `Assisted-by` tag detailing the source (see Section 4).

### Type 3: Uncopyrightable Edits to Copyrighted Code
* **Definition:** Purely AI-generated refactors, or Public Domain edits, applied to an existing file that contains copyrighted human code.
* **Action:** Retain the file's existing SPDX License Identifier. The file as a whole remains a derivative work bound by the original license.
* **Commit Message:** Requires `Signed-off-by` **AND** an `Assisted-by` tag.

### Type 4: Copyrightable Human Edits to Uncopyrightable Code
* **Definition:** Substantive, creative human fixes or additions applied to an existing file that was previously entirely AI-generated or Public Domain.
* **Action:** The human edits inject copyright into the file. You **must add** the appropriate SPDX License Identifier (`Apache-2.0` or `CC-BY-4.0`) to the file header.
* **Commit Message:** Standard `Signed-off-by` required.

## 4. Attribution for AI and Public Domain Sources

When utilizing Generative AI or introducing Public Domain material (for Type 2 and Type 3 commits), proper attribution is required in the commit message to track the evolving provenance of the codebase.

Contributions utilizing AI should include an `Assisted-by` tag in the following format:

`Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]`

* `AGENT_NAME`: The name of the AI tool or framework.
* `MODEL_VERSION`: The specific model version used.
* `[TOOL1] [TOOL2]`: Optional specialized analysis tools used.

*(Note: Basic development tools like git, gcc, make, or IDEs should not be listed.)*

**Example of a Type 3 Commit Message:**
```text
Refactor network routing logic for efficiency

The core loop in network_router.c was rewritten to reduce memory overhead. 
This was generated as a draft and inserted without substantive human modification.

Signed-off-by: John Smith <john.smith@example.com>
Assisted-by: Claude:claude-3-opus
