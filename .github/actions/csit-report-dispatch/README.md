# 🛠️ CSIT Report Dispatch Matrix

Generates a GitHub Actions matrix for environments based on the selected node
configuration and DUT type.

## Usage Example

An example workflow step using this action:

<!-- markdownlint-disable MD013 -->
```yaml
- name: Prepare node selection matrix
  uses: fdio/csit/.github/actions/csit-report-dispatch@master
```
<!-- markdownlint-enable MD013 -->

## Inputs

<!-- markdownlint-disable MD013 -->

| Variable Name | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| node          | CSIT bootstrap node identifier (e.g., 2n-icx, 3n-snr, etc.). |
| dut           | Target DUT type (e.g., vpp, dpdk, trex).                     |

<!-- markdownlint-enable MD013 -->

## Outputs

<!-- markdownlint-disable MD013 -->

| Variable Name | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| output        | JSON matrix object for GitHub Actions workflow.              |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

Jq binary required to be installed on executor image.