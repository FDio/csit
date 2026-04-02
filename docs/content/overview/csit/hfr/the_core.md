---
title: "The Core"
weight: 1
---

# Managing the testing jobs

## Main principles

1. Start a run only if there is a testbed available for it.
   a. No (or minimal amount of) runs waiting for a testbed.
   b. No waste of executors.
2. Periodically monitor the state of runs.
   a. Optimise the utilisation of testbeds.
   b. Minimise the overall testing time.
3. Accept the runs not started by HFR.
   a. E.g. periodical runs can run independently on runs managed by HFR.
4. Provide actual information about all runs and testbeds managed by HFR.
   a. Operational data is updated periodically and it is available all the time.

## States of the testing jobs and transitions between states

The run can be in one of these five states:
- queued
- started
- running
- canceled
- finished

### Run state: queued

This is an the initial state of each run. The run is in HFR queue (not GHA
queue) to be started immediately when there is an available testbed for it.

Possible transitions:
1. queued -> queued
   - If there is no accessible testbed, stay in the same state.
2. queued -> started
   - If there is an accessible testbed:
     - pre-reserve the testbed in HFR (not directly on the testbed, this will be
       implemented in the next phase), to avoid reservation by another run,
     - start the run in GHA.

### Run state: started

The run has been started in GHA. It is “queued” (waiting for an executor) or
“in-progress” in GHA and waiting for a testbed.

Possible transitions:
1. started -> started
   - If the run is not running on GHA executor or
   - it is waiting for a testbed.
2. started -> running
   - The run is running on GHA executor and it is running on a testbed.
3. started -> finished
   - If the run finished. This can happen if the HFR period is too long and the
     testing run too short. It is a correct behaviour.
4. started -> canceled
   - If the run was canceled either by GHA, HFR or manually.

### Run state: running

The run is running on a testbed.

Possible transitions:
1. running -> running
   - If the run still runs on the testbed (no change in the testbed nor GHA
     status).
2. running -> canceled
   - If the run was canceled either by GHA, HFR or manually.
3. running -> finished
   - If the run finished.

### Run state: canceled

The run has been canceled either by GHA, HFR or manually.

Possible transitions:
1. cancelled -> queued
2. cancelled -> finished

If "re-run" is enabled and the max count is not reached, change the status to
"queued" and increase the counter of runs. Otherwise change the status to
"finished".

### Run state: finished

The run finished, clean everything.

## Run management loop

The procedure depicted in the next flow chart is repeated periodically until all
pre-defined runs are in the state “finished”. The time period of these
repetitions is set in the HFR configuration file.

{{< figure src="/cdocs/HFR_run_management.svg" >}}
