# Contributing to this Project

First off, thank you for considering contributing! We value all contributions,
whether they are bug fixes, new features, or documentation updates.

To ensure the legal integrity of this project and protect both our contributors
and downstream users, we have established guidelines for licensing, provenance
tracking, and the use of Generative AI.

## 1. Licensing Overview

This project uses specific licenses for code and documentation. Please refer to
the central LICENSE file in the repository root for the exact license terms.

We track licensing at the file level using SPDX License Identifiers. Files
containing human-authored, copyrightable material must include the appropriate
SPDX header at the top of the file.

## 2. Developer Certificate of Origin (DCO)

We require all contributions to comply with the Developer Certificate of Origin
(DCO). You can read the current version of the DCO at:
[https://developercertificate.org/](https://developercertificate.org/)

To certify your compliance, every commit must include a `Signed-off-by` line in
the commit message.

Requirements for Signed-off-by:
* The signing entity must be a human person. AI agents, bots, and automated
  tools cannot legally certify the DCO.
* You must use a valid personal or corporate e-mail address. Group aliases or
  mailing lists are not permitted.
* By adding this line, you are taking full legal responsibility for the
  contribution and affirming that you have the right to submit it under the
  project's licenses, including any external copyrighted code.

## 3. Default Authorship and Disclaimers

With the rise of Generative AI and the inclusion of Public Domain code, tracking
the provenance of our codebase is critical.

By default, signing the DCO implies you are the human author and copyright
holder of the entire commit.

If your commit includes code where you are NOT the sole human copyright owner
(e.g., Generative AI outputs, Public Domain snippets, or third-party
permissively licensed code), you must explicitly disclaim those parts in the
Git commit message. (Note: Submitting third-party licensed code is already
governed by the DCO, but its presence must still be clearly documented here).

We do not enforce a strict formatting syntax for this disclaimer. You may use
natural language narrative, community-standard Git trailers (like `Assisted-by:`
or `Co-authored-by:`), or a combination of both.

The only requirement is that a subsequent human reviewer or auditor reading the
commit message can reasonably understand which parts of the diff are your
copyrighted additions, and which parts originate from an uncopyrightable or
external source.

## 4. Examples of Provenance Tracking

Below are three examples demonstrating how to properly document mixed-provenance
commits in your commit messages.

### Example A: AI Base + Human Fixes

```text
Add fast-path JSON parser for telemetry data

The initial boilerplate and the core tokenization loop were drafted
using generative AI.

I manually rewrote the `handle_malformed_input` function and the
memory allocation logic to fix a segfault and align with our internal
API standards.

Signed-off-by: Alex Chen <alex.chen@example.com>
Assisted-by: Claude:claude-3-opus
```

### Example B: External Public Domain + Human Wrappers

```text
Implement orbital trajectory calculation module

Added the `orbital_math.c` core algorithm. This algorithm was originally
authored by NASA (US Government) and is in the Public Domain.

The C++ wrapper classes (`TrajectoryCalculator.cpp` and `.h`) and all
associated unit tests are original human-authored additions.

Signed-off-by: Jamie Rivera <j.rivera@example.com>
```

### Example C: Human Core Logic + AI Linting/Refactoring

```text
Introduce rate limiting middleware

All core logic, state management, and Redis integrations are original
human-authored code.

An AI agent was used to perform a non-substantive refactor: adding
docstrings, formatting the code to pass our linter, and simplifying
the `switch` statement in the config parser.

Signed-off-by: Sam Taylor <sam.taylor@example.com>
Co-authored-by: GitHub Copilot
```
