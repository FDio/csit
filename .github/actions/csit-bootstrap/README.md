# 🛠️ CSIT Bootstrap

Runs CSIT bootstrap script of choice. Optionally runs on top of oper branch.

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
- name: CSIT Bootstrap
  uses: fdio/csit/.github/actions/csit-bootstrap@master
```
<!-- markdownlint-enable MD013 -->

## Inputs

<!-- markdownlint-disable MD013 -->

| Variable Name    | Description                            |
| ---------------- | -------------------------------------- |
| bootstrap_script | CSIT bootstrap script to source.       |
| with_oper        | Use oper branch to checkout the code.  |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

CSIT repository needs to be checkout.