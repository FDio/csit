# 🛠️ Setup Executor Environment

Action to setup FD.io Nomad executor environment inside a GitHub action/workflow

## setup_executor_env

## Usage Example

```yaml
- name: "Setup Environment"
  uses: fdio/csit/.github/actions/setup_executor_env@master
```

<!-- markdownlint-enable MD013 -->

## Outputs

The action has no outputs, but does provide summary step information when
invoked.

## Requirements/Dependencies

The git command-line tool must be available in the environment for the action
to succeed.