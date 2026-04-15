# 🛠️ CSIT Bootstrap

Runs CSIT bootstrap script of choice after fetching origin.
Optionally runs on top of oper branch or a specific refspec.

## Requirements/Dependencies

An older state of CSIT repository needs to be locally present already,
for example in a mounted docker container.

## Inputs

<!-- markdownlint-disable MD013 -->
| Variable Name    | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| path             | Path to the root of an existing old clone of CSIT repository. |
| git_branch       | Git branch to use for oper branch detection or script code.   |
| csit_ref         | CSIT refspec to checkout if oper is not desired.              |
| with_oper        | Checkout newest oper branch, only if csit_ref is empty.       |
| bootstrap_script | CSIT bootstrap script to run.                                 |
<!-- markdownlint-enable MD013 -->

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
  - name: Run CSIT Bootstrap
    # yamllint disable-line rule:line-length
    uses: fdio/csit/.github/actions/csit-bootstrap@{pinned_hash}  # Version x.y
    with:
      path: vpp/csit
      csit_ref: {{ env.CSIT_REF }}
      with_oper: false
      bootstrap_script: bisect.sh
```
<!-- markdownlint-enable MD013 -->

