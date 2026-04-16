# FDio Fetch and maybe Bootstrap

After fetching from remote origin, execute bootstrap script if specified.
Optionally uses head of the newest oper branch, or a specified refspec.

## Concerns

This single action combines two otherwise separate concerns,
three if oper branch selection is treated as separate from script execution.

This is deliberate, as it simplifies call sites,
and CSIT does not have to support usage not conforming
to the fetch&bootstrap pattern as defined in this action.

The concerns are implemented as bash blocks in steps of the combined action.
Division into elementary sub-actions would be cleaner
from the documentation point of view,
but it would also introduce hassle when bumping commit hashes
(one change for sub-action, merge, copy the generated hash
into the combined action, merge again) that is not worth it.

Input fields are flexible enough to enable also VPP fetch.

## Requirements

An older state of the git repository needs to be locally present already,
for example in a mounted docker container.

The remote "origin" there has to be configured properly already,
which currently means pointing to the github mirror and not to the gerrit server.

## Dependencies

No GHA dependencies.

## Inputs

<!-- markdownlint-disable MD013 -->
| Input name | Default value    | Description                                                     |
| ---------- | ---------------- | --------------------------------------------------------------- |
| repo_dir   |                . | Path to the root of an existing old clone of a git repository.  |
| git_branch |    origin/master | Git branch to use for oper branch detection or script code.     |
| refspec    |   (empty string) | CSIT refspec to checkout, empty if git_branch HEAD is fine.     |
| depth      |   (empty string) | Limit fetch depth, unlimited if empty.                          |
| with_oper  |            false | Checkout newest oper branch, only if refspec is empty.          |
| script     |       (required) | Filename of CSIT bootstrap shell script to execute if nonempty. |
| log_file   |        fetch.log | File to store console logs, path is relative to repo_dir.       |
| tui_line   | (28 equal signs) | Visually apparent string to guide humans reading the logs.      |
<!-- markdownlint-enable MD013 -->

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
  - name: Fetch VPP
    # yamllint disable-line rule:line-length
    uses: fdio/csit/.github/actions/fetch-and-maybe-bootstrap@{pinned_hash}  # Version x.y
    with:
      repo_dir: ${{ env.DOCKER_ROOT }}/vpp
      refspec: ${{ env.VPP_REF }}
      log_file: ${{ env.LOG_DIR }}/vpp.log
  - name: Fetch and Bootstrap CSIT
    # yamllint disable-line rule:line-length
    uses: fdio/csit/.github/actions/fetch-and-maybe-bootstrap@{pinned_hash}  # Version x.y
    with:
      repo_dir: ${{ env.DOCKET_ROOT }}/csit
      refspec: ${{ env.CSIT_REF }}
      depth: 1
      with_oper: true
      script: bisect.sh
      log_file: ${{ env.LOG_DIR }}/csit.log
```
<!-- markdownlint-enable MD013 -->

## Implementation details

If with_oper is true (and refspec empty), fetch uses --all to see oper branches.
Otherwise, the fetch step uses --tags instead, and targets git_branch only.

If respec is not empty, oper branch checkout is always skipped,
because that avoids the heavier fetching.

The current working directory is left at repo_dir.

Both steps are logging into the same file.

## Caveats

In workflows with multiple calls, do not forget to change log_file value
to avoid overwriting the logs from earlier calls.

Obviously, VPP repo does not contain bootstrap scipts,
and it also has no oper branches,
so skip the related inputs when fetching VPP repo.

Do not limit depth when VPP fetch should leave repo in a state
where version string construction has to work,
as "git describe" needs to see all the commits since the latest git tag.

The current implementation details do not allow verifying
edits to with_oper_for_vpp.sh CSIT wrapper directly before merging.
But the verification is still possible indirecty,
using an add-hoc bootstrap script that calls the wrapper.
