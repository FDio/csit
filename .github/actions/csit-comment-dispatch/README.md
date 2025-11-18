# 🛠️ CSIT Comment Dispatch

Generates a GitHub Actions matrix for environments based on the selected node
configuration and DUT type.

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
- name: Prepare node selection matrix
  uses: fdio/csit/.github/actions/csit-comment-dispatch@master
```
<!-- markdownlint-enable MD013 -->

## Inputs

<!-- markdownlint-disable MD013 -->

| Variable Name  | Description                            |
| -------------- | -------------------------------------- |
| gerrit_comment | Full command line from Gerrit comment. |

<!-- markdownlint-enable MD013 -->

## Outputs

<!-- markdownlint-disable MD013 -->

| Variable Name | Description                                     |
| ------------- | ----------------------------------------------- |
| matrix        | JSON matrix object for GitHub Actions workflow. |
| params        | Parameters for workflow.                        |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

Jq binary required to be installed on executor image.