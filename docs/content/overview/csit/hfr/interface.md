---
title: "Interface"
weight: 4
---

# Interface

## Interface to GHA

Interface to GitHub Actions uses [GHA REST API](https://docs.github.com/en/rest)
and implements methods to:
- start a run,
- get the status of a run,
- cancel a run (normal or force).

## Interface to Testbeds

The HFR uses existing set of testbeds and communicates with them via ssh channel
using bash commands. It implements methods to:
- get the status of testbed(s)
- find an available testbed,
- unreserve a testbed.

### The data structure

The operational status of all testbeds is represented by a list where each item
represents one testbed.

```python
[
    Testbed(
        name=str(),
        node=str(),
        tg=dict(),
        status=str(),
        pre_reserved_by=str(),
        job=str(),
        run_id=str()
    ),
    Testbed()
]
```

**Testbed**
- name - The name of the testbed as it is defined in its topology file.
- node - node-arch identificator, e.g.: 2n-spr.
- tg - All necessary information about the testbed's traffic generator as it is
  defined in the topology file. This information is used to communicate with the
  testbed.
- status - The status of the testbed:
  - available,
  - pre-reserved (by HFR),
  - reserved,
  - unreachable.
- pre_reserved_by - HFR ID of a run which is planned for this testbed. Note that
  the run can finally run on a different testbed as pre-reserved for it.
- job - the job name (only for status == reserved, otherwise None).
- run_id - The ID of a run (only for status == reserved, otherwise None).

**Example** (no run on this testbed):

```json
        "tb": {
            "name": "lf_2n_zn2_testbed210",
            "node": "2n-zn2",
            "tg": {
                "type": "TG",
                "subtype": "TREX",
                "model": "Amd-EpycZen2",
                "host": "10.30.51.61",
                "arch": "x86_64",
                "port": 6001,
                "username": "testuser",
                "password": "Csit1234"
            },
            "status": "available",
            "pre_reserved_by": "0796401351",
            "job": null,
            "run_id": null
```

## Data presentation

Presentation of data produced by tests run by testing jobs.

See [C-Dash](https://csit.fd.io/)
