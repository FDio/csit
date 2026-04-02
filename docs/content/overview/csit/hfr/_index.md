---
bookCollapseSection: true
bookFlatSection: false
title: "Hands-Free Releasing"
weight: 6
---

# Hands-Free Releasing - Top Level View

The HFR consists of:
- **HFR core** - Manages the testing runs using information from its
  peripherals. It processes the input data, generates the actions and performs
  them.
- **Interfaces** - Bi-directional communication with peripherals.

## The Diagram

{{< figure src="/cdocs/HFR_top_level_view.svg" >}}

### The Core

The HFR core is responsible for:
- Processing the data from inputs (status of testbeds and testing runs,
  configuration and operational data)
- Evaluation of current state of testbeds and testing runs
- Generating actions:
  - Testing runs - starting, cancelling, checking the status, ….
  - Testbeds - checking the status, (un)reservation (next phase)….
  - Writing operational data to the storage
- Monitoring
- Availability of operational data

### Testbeds and interface to testbeds

- Uses existing set of testbeds
- Interface
  - ssh channel
  - bash commands
- Tasks performed on the testbeds (next phase):
  - reservation and voiding of testbeds
  - TG and DUTs health

### GitHub Actions and interface to GHA

Must be able to:
- start a run with parameters
- check a run status
- cancel a run

Interface
- [GHA REST API](https://docs.github.com/en/rest)

### Data storage and interface to data storage

Configuration of HFR and runs
- GitHub
  - the configuration files are part of code
  - possibility to store more than one configuration (e.g. rc1, rls, …)
- File system of the executor
  - Operational data (current status of HFR and runs).

## Managing the testing runs

HFR does not run any tests, it manages the testing runs and resources (testbeds
and GHA runs) used by those testing runs.

{{< figure src="/cdocs/HFR_testing_jobs_processing.svg" >}}

The blue box is explained in the chapter [The Core]({{< relref "the_core" >}})

### The lifecycle of the testing run

- Pick the run from the list of runs sorted by priority.
- If there is an available testbed for it, start it.
- The run is queued in GHA, waiting for an executor.
- The run started in GHA and reserves the testbed.
- The run runs tests on the testbed.
- The run finishes testing on the testbed.
- The run releases the testbed.
- The run writes the results of tests (JSON files and logs) to the storage.
- The run finishes.
