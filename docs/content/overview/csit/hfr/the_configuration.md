---
title: "The Configuration"
weight: 2
---

# The Configuration

The configuration is divided into two parts:

- configuration of HFR system itself,
- configuration of the testing process which includes (not only):
  - testbeds,
  - testing runs,
  - priorities,
  - parameters of the testing runs, …

The configurations are:
  - structured,
  - human and machine readable,
  - both configurations are stored in GitHub repository in YAML format.

## HFR Configuration

The application configuration is read from two sources:
1. environment
2. configuration file.

All listed parameters are mandatory if it is not marked "optional".

1. Environment
   - GITHUB_URL
   - GITHUB_ACCOUNT
   - GITHUB_REPO
   - GITHUB_PAT
   - PATH_CONFIG
2. Configuration file
   - logging_level
   - sleep_interval
   - re_run_canceled (optional) - run again cancelled runs
   - nr_of_re_runs (optional) - number of re-runs of cancelled runs
   - max_waiting_time (optional) - max time while a run waits for a testbed
   - run_config - path to the run configuration file
   - oper_data - path to the operational data
   - csv_data - a path to the csv file to save selected parameters
   - testbed_data - a path to the csv file to save the current state of testbeds
   - run_log_url (optional) - base URL to run logs
   - keep_old_oper_data (optional)
   - dir_testbeds - path to the testbeds specifications

### Example of the configuration file

```yaml
logging_level: "INFO"
sleep_interval: 120  # seconds

re_run_canceled: True
nr_of_re_runs: 3
max_waiting_time: 600  # minutes
max_gha_retries: 3

run_config: "hfr/configuration/run_conf.yaml"

oper_data: "hfr/oper/data.json"
csv_data: "hfr/oper/data.csv"
testbed_data: "hfr/oper/testbeds.csv"

run_log_url: "https://logs.fd.io/vex-yul-rot-jenkins-1"

keep_old_oper_data: False

dir_testbeds: "hfr/topologies"
```

### Structure of application configuration data after processing

```json
{
    "github": {
        "url": "str",
        "account": "str",
        "repo": "str",
        "pat": "str"
    },
    "app": {
        "path_config": "str",
        "logging_level": "str",
        "sleep_interval": "int",
        "re_run_canceled": "bool",
        "nr_of_re_runs": "int",
        "max_waiting_time": "int",
        "run_config": "str",
        "oper_data": "str",
        "testbed_data": "str",
        "run_log_url": "str",
        "keep_old_oper_data": "bool",
        "dir_testbeds": "str"
    }
}
```

## Testing Process Configuration

The run configuration consists of two parts:
- workflows - defines workflows
- parameters - defines the way how the runs specified in this configuration file
  will be processed.

### Workflows

Each workflow has its runs and parameters.

**runs**:
- inputs - The variables and their values which are then passed to the workflow
  run. All inputs required by the workflow must be listed here. They are passed
  to the workflow whne it is started without any processing.
- params:
  - prio - priority of the run: 1 - highest priority, 9 - lowest priority.
  - repeat - how many times the run is run. Typically it is 1 for coverage jobs
    and 10 for iterative jobs. The valid value is from 1 to 20.

**parameters**:
- name - the name of a run as it is set in GHA workflow yaml file.
- ref - The branch with the workflow, usually "master".
- needed_params - the list of parameters which must be present in 'inputs'
  section of each run in the workflow. This list is used to validate the run's
  definitions.

### Parameters

Parameters in this section say how the runs will be processed:
- queuing: one of "sequential", "mixed" or "random". This parameter says how the
  runs will be queued depending on their priority:
  - sequential - Runs are only sorted by priority, e.g. if there are 10 mrr and
    10 ndrpdr runs with the same priority we get list of 10 mrr runs followed by
    10 ndrpdr runs.
  - mixed - Runs are sorted by priority and then the runs with the same priority
    are mixed, e.g. if there are 10 mrr and 10 ndrpdr runs with the same
    priority we get list: [mrr, ndrpdr, mrr, ndrpdr, ..., ndrpdr].

### Example of the run configuration

```yaml
workflows:
  csit-hfr:
    runs:
      # 2n-icx
      - inputs:
          job_type: "coverage"
          dut: "vpp"
          node: "2n-icx"
          branch: "rls2602"
          suite_gen_params: "#2n-icx-vpp-cov-ip4-hfr #mrr"
        params:
          prio: 1
          repeat: 2
      # 2n-zn2
      - inputs:
          job_type: "coverage"
          dut: "vpp"
          node: "2n-zn2"
          branch: "rls2602"
          suite_gen_params: "#2n-zn2-vpp-cov-ip4-hfr #mrr"
        params:
          prio: 3
          repeat: 2
    parameters:  # Workflow parameters
      name: "csit-{dut}-perf-report-{job_type}-{branch}-{node}"
      ref: "master"
      needed_params:
        - "job_type"
        - "dut"
        - "node"
        - "branch"
        - "suite_gen_params"
parameters:  # Global parameters
  queuing: "mixed"
```

### The structure of the run configuration after processing

```python
{
    "node_1": [
        Run(
            workflow=str(),
            inputs={
                "job_type": str(),
                "dut": str(),
                "node": str(),
                "branch": str(),
                "suite_gen_params": str()
            },
            "name": str(),
            "ref": str()
        ),
        Run(),

    ],
    "node_2": list(),

}
```

The runs are grouped by the node and sorted by the priority and the parameter
'queuing'.
