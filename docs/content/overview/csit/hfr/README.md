---
title: "Read Me"
weight: 1
---

# Hands-Free Releasing (HFR)

Hands-Free Releasing (HFR) dispatches a configured set of CSIT GitHub Actions
workflows, assigns runs to available testbeds, tracks their status, and writes
operational summaries. It is a long-running Python process; it does not expose
an HTTP service or a command-line interface beyond starting the application.

{{< figure src="/cdocs/hfr-architecture.svg" >}}

## How it works

`docker-hfr-dispatcher/app.py` loads application and run configuration, reads
testbed topology YAML files, and initializes operational state. The
`RunManagement` loop refreshes testbed status, starts queued workflow runs when
a matching testbed is free, polls GitHub Actions, and writes updated state on
each iteration. The interval is controlled by `sleep_interval`.

| Component | Responsibility |
| --- | --- |
| `hfr/app_configuration.py` | Reads GitHub settings from environment variables and application settings from YAML. |
| `hfr/run_configuration.py` | Validates and expands workflow run definitions and queue order. |
| `hfr/intf_gha.py` | Calls GitHub Actions workflow dispatch, run status, and cancellation endpoints. |
| `hfr/intf_tb.py` and `hfr/ssh.py` | Reads CSIT topology files and checks testbed availability over SSH. |
| `hfr/run_management.py` and `hfr/oper_data.py` | Manages run states and persists JSON/CSV operational data. |

HFR dispatches a workflow with its configured `ref` and `inputs`, then finds or
polls its GitHub run. HFR checks traffic-generator hosts for
`/tmp/reservation_dir/` on each TG to determine testbed availability. Runs move
through
`queued`, `started`, `running`, `cancelled`, and `finished` states. Runs that
stay queued at GitHub too long or wait too long for a testbed can be cancelled;
cancelled runs may be re-queued when configured. See
[`run_management.py`](docker-hfr-dispatcher/hfr/run_management.py) for the
state transitions and timeout behavior.

The main integrations and configuration are in
[`intf_gha.py`](docker-hfr-dispatcher/hfr/intf_gha.py),
[`intf_tb.py`](docker-hfr-dispatcher/hfr/intf_tb.py), and
[`app_conf.yaml`](docker-hfr-dispatcher/hfr/configuration/app_conf.yaml).

## Requirements and local development

- Python 3.13 or newer and [uv](https://docs.astral.sh/uv/). The project pins
  Python 3.13 in
  [`.python-version`](docker-hfr-dispatcher/.python-version); dependencies are
  declared in [`pyproject.toml`](docker-hfr-dispatcher/pyproject.toml) and
  locked in [`uv.lock`](docker-hfr-dispatcher/uv.lock).
- A GitHub personal access token in `GITHUB_PAT` with access to dispatch and
  inspect the configured repository's Actions workflows. Cancellation also
  uses the Actions runs API.
- CSIT topology YAML files in the directory configured by `dir_testbeds`.
  The repository's Docker build workflow obtains these from
  `fdio/csit/topologies/available`; they are not checked in here.
- Reachability from the dispatcher to the GitHub API and to the testbed
  traffic-generator hosts over SSH, using the access configuration in each
  topology file.

From the repository root:

```sh
cd docker-hfr-dispatcher
uv sync
export GITHUB_PAT='<token>'
uv run app.py
```

The process uses the current working directory to resolve relative config and
topology paths. By default it reads `hfr/configuration/app_conf.yaml`, which
selects `hfr/configuration/run_conf_*.yaml`; set `PATH_CONFIG` to use another
application config. For direct local execution, also ensure the configured
`dir_testbeds` directory contains the topology files. `uv run app.py` runs
continuously until all configured runs finish or startup fails.

The checked-in Compose file references `../.env` and does not mount a data
volume. As written, its `build`, `command`, and `env_file` keys sit directly
under `services` without a service name, so it does not appear to define a
valid Compose service. If that structure is corrected locally, the apparent
intended invocation is:

```sh
cd docker-hfr-dispatcher
docker compose up --build
```

Create the referenced root `.env` file with `GITHUB_PAT` and any optional
environment overrides. The image runs `uv run app.py` from `/app`. The default
`/data` operational files are not persisted across container recreation
unless you add a volume.

## Configuration

Environment variables are read before the application YAML. The application
YAML provides run-management settings and paths.

| Setting | Source | Default / behavior |
| --- | --- | --- |
| `GITHUB_PAT` | Environment | Required; empty by default. |
| `GITHUB_URL` | Environment | `https://api.github.com` |
| `GITHUB_ACCOUNT` | Environment | `repos` (the API path prefix, yielding `/repos/<repo>`). |
| `GITHUB_REPO` | Environment | `fdio/csit` |
| `PATH_CONFIG` | Environment | `hfr/configuration/app_conf.yaml` |
| `PATH_OPER` | Environment | `/data`; base directory for operational JSON/CSV files. |
| `logging_level` | Application YAML | `INFO`; supported values are Python logging levels. |
| `sleep_interval` | Application YAML | `30` seconds; values outside 5–3600 are reset to 30. |
| `run_config` | Application YAML | Required; the checked-in default file selects `run_conf_rc2.yaml`. |
| `dir_testbeds` | Application YAML | Required; path to topology YAML files. |
| `oper_data`, `csv_data`, `testbed_data` | Application YAML | Under `PATH_OPER`; default to `hfr_oper/data.json`, `hfr_oper/data.csv`, and `hfr_oper/testbeds.csv`. |
| `re_run_cancelled` | Application YAML | `False`. |
| `nr_of_re_runs` | Application YAML | `3`. |
| `max_gha_retries` | Application YAML | `3` retries when a run cannot be found or queried. |
| `max_waiting_time` | Application YAML | `600` minutes waiting for a testbed. |
| `run_log_url` | Application YAML | `https://logs.fd.io/vex-yul-rot-jenkins-1`. |
| `keep_old_oper_data` | Application YAML | `False`; when enabled, existing JSON state is loaded and resumed. |

The environment variable values above are defined in
[`constants.py`](docker-hfr-dispatcher/hfr/constants.py). The checked-in
application YAML uses `DEBUG`, a 180-second interval, cancelled-run retries,
and `run_conf_*.yaml`; those file values override the code defaults.

Run configuration YAML has a top-level `workflows` mapping. Each workflow
defines `runs` with workflow `inputs` and HFR `params` such as `prio` and
`repeat`, plus workflow-level `parameters` including the run `name` template,
GitHub `ref`, and `needed_params`. Top-level `parameters.queuing` accepts
`sequential`, `mixed`, or `random`. A list-valued `suite_gen_params` expands
into separate runs. HFR adds `hfr_run_id` to workflow inputs when dispatching.
Examples are in [`hfr/configuration`](docker-hfr-dispatcher/hfr/configuration/).

Testbed topology YAMLs are consumed by `intf_tb.py`; each needs a `nodes.TG`
entry containing the traffic-generator connection details, including `host`
and `port`. The code removes any `interfaces` entry before using the TG data.

## Interfaces and data

HFR has no inbound API. Its external interface is the GitHub Actions REST API
for the configured repository:

| Operation | Request |
| --- | --- |
| Dispatch | `POST /repos/{owner}/{repo}/actions/workflows/{workflow}.yml/dispatches` with `{"ref": ..., "inputs": {...}}`. |
| Discover a run | `GET /repos/{owner}/{repo}/actions/workflows/{workflow}.yml/runs`; HFR matches its generated run name. |
| Poll a known run | `GET /repos/{owner}/{repo}/actions/runs/{run_id}`. |
| Cancel | `POST /repos/{owner}/{repo}/actions/runs/{run_id}/cancel` or `/force-cancel`. |

Requests use the token from `GITHUB_PAT` and a 10-second timeout. Request or
JSON failures are logged and handled as unsuccessful responses; repeated
missing GitHub run data eventually marks the run with an HFR `gha_failure`.
See [`intf_gha.py`](docker-hfr-dispatcher/hfr/intf_gha.py).

Operational files are written under `PATH_OPER` (default `/data`):

- `hfr_oper/data.json` stores the configured runs and their HFR/GitHub state;
  `keep_old_oper_data: true` resumes this state.
- `hfr_oper/data.csv` contains a report-oriented subset, including DUT, node,
  testbed, run URL/status/conclusion, log URL, timestamps, duration, and HFR
  status/conclusion.
- `hfr_oper/testbeds.csv` records testbed name/status, associated run, host,
  and port.

The run CSV's `Log` column is consumed by the separate
[`process_reports.py`](process_reports.py) script. That script fetches
`report.html.gz` beneath each log URL, extracts total/pass/fail counts and
failed test names, and adds `Total`, `Pass`, `Fail`, and `Failed tests`
columns. It resumes rows that already have `Total` and writes progress back
incrementally. It takes no command-line path argument: it always opens
`data.csv` in the current working directory. Run it from a directory where
the HFR CSV has been copied or named `data.csv`:

```sh
python /path/to/hfr-nomad-docker/process_reports.py
```

## Build and deployment

The Docker image is built from the
[`Dockerfile`](docker-hfr-dispatcher/Dockerfile) using the Astral uv Python
3.13 slim base image. The
[Docker Bake target](docker-hfr-dispatcher/docker-bake.hcl) builds for
`linux/amd64` and `linux/aarch64`. The
[GitHub Actions workflow](.github/workflows/docker.yml) builds on pull
requests and pushes to `master` or `v*` tags; it checks out CSIT to copy
available topology YAML files before building. Pull requests build without
publishing; pushes authenticate to Docker Hub and publish metadata tags for
`pmikus/docker-hfr-dispatcher-prod`.

[`terraform-nomad-hfr-dispatcher/main.tf`](terraform-nomad-hfr-dispatcher/main.tf)
defines the Nomad batch job resource. Terraform selects a Nomad jobspec by
dispatcher version, passes image/resource/namespace variables, and connects to
the configured Nomad provider and Consul backend. The
[master jobspec](terraform-nomad-hfr-dispatcher/nomad-hfr-dispatcher-master.hcl)
injects values from Nomad variable path `nomad/jobs` into the task's `.env` and
mounts a host data volume at `/data/` by default. The runtime is one dispatcher
task; the job spec sets one allocation and no restart attempts.

Deployment files have version-specific differences and should be checked
before use. For example, the `2606.0` jobspec references `var.volume_source`
without declaring that variable, while the `master` jobspec declares it. The
Terraform provider and Consul backend addresses are also hard-coded in the
checked-in configuration. The Terraform subdirectory README appears to
describe a different dispatcher and does not match the current Terraform
sources.

## Operations and troubleshooting

- Logs go to standard output with timestamps and levels. Set `logging_level`
  to `DEBUG` for iteration and state-transition detail. There is no health
  endpoint or metrics exporter in this repository.
- Startup stops with a logged error if configuration cannot be read, the run
  config is invalid, required topology files are absent, or operational data
  cannot be initialized.
- If a testbed appears unavailable or unreachable, check the TG host/port in
  its topology YAML, SSH connectivity/credentials, and the reservation state
  under `/tmp/reservation_dir/` on that host.
- If runs are not dispatched or status is missing, check `GITHUB_PAT`, the
  configured GitHub URL/account/repository, workflow file names, `ref`, and
  workflow inputs. GitHub API failures are logged as warnings; retries are
  controlled by `max_gha_retries`.
- If operational files disappear after a container restart, ensure `/data`
  is backed by a persistent volume. Check `PATH_CONFIG`, `PATH_OPER`, and
  configured relative paths against the process working directory.

There are no application tests checked into this repository. The Docker CI
workflow validates image builds; it does not run a Python test suite.
