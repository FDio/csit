# CSIT Fetch

Freshens existing local CSIT repository and checks out master,
so oper branch detection works correctly.

## Usage Example

An example workflow step using this action:

<!-- markdownlint-enable MD013 -->

FIXME: Copy real code when applied to bisect workflow.

## Inputs

<!-- markdownlint-disable MD013 -->

| Variable Name    | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| path             | CSIT repository path to the pre-checkouted old clone of CSIT repo. |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

Older state of CSIT repository needs to be pre-perared, for example in a mounted docker container.
