# 🛠️ Setup Executor Environment

Action to setup FD.io Nomad executor environment inside a GitHub
action/workflow.

## Usage Example

Sets the OS details used for Git operations inside other actions/workflows.

<!-- markdownlint-disable MD013 -->
```yaml
- name: "Setup Environment"
  uses: fdio/csit/.github/actions/setup_executor_env@master
```
<!-- markdownlint-enable MD013 -->

## Outputs

<!-- markdownlint-disable MD013 -->

| Variable Name   | Description                     |
| --------------- | ------------------------------- |
| OS_ID           | Operating system ID.            |
| OS_VERSION_ID   | Operating system Version ID.    |
| OS_ARCH         | Operating system architecture.  |

<!-- markdownlint-enable MD013 -->

## Requirements/Dependencies

The git command-line tool must be available in the environment for the action
to succeed.