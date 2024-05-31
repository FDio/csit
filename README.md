# CSIT - Continuous System Integration Testing

1. [Architecture](#architecture)
1. [Directory Structure](#directory-structure)
   1. [Tests](#tests)
   1. [Keywords](#keywords)
   1. [Other Resources](#other-resources)
1. [CSIT Interactive Dashboard](#csit-interactive-dashboard)
1. [CSIT Documentation](#csit-documentation)

## Architecture

FD.io CSIT system design needs to meet continuously expanding requirements of
FD.io projects including VPP, related sub-systems (e.g. plugin applications,
DPDK drivers) and FD.io applications (e.g. DPDK applications), as well as
growing number of compute platforms running those applications. With CSIT
project scope and charter including both FD.io continuous testing AND
performance trending/comparisons, those evolving requirements further amplify
the need for CSIT framework modularity, flexibility and usability.

CSIT follows a hierarchical system design with SUTs and DUTs at the bottom level
of the hierarchy, presentation level at the top level and a number of functional
layers in-between. The current CSIT system design including CSIT framework is
depicted in the figure below.

## Directory Structure

### Tests

```
.
└── tests
    ├── dpdk
    │   └── perf                    # DPDK performance tests
    ├── trex
    │   └── perf                    # TRex performance tests
    └── vpp
        ├── device                  # VPP device tests
        └── perf                    # VPP performance tests
```

### Keywords

```
.
resources
└── libraries
    ├── bash
    │   ├── entry                   # Main bootstrap entry directory
    │   └── function                # Bootstrap function library
    ├── python                      # Python L1 KWs
    └── robot                       # Robot Framework L2 KWs
```

### Other Resources

```
.
│── csit.infra.dash                 # CDash code
│── csit.infra.etl                  # ETL pipeline code
│── csit.infra.hugo                 # CDocs local provisioning
│── csit.infra.vagrant              # VPP device vagrant environment
├── docs                            # Main documentaion
|── fdio.infra.ansible              # Infrastructure provisioning
|── fdio.infra.packer               # Infrastructure provisioning
|── fdio.infra.pxe                  # Preboot eXecution Environment
|── fdio.infra.terraform            # Virtual infrastructure provisioning
|── GPL                             # Files licensed under GPL
│   ├── traffic_profiles            # Performance tests traffic profiles
│   └── traffic_scripts             # Functional tests traffic profiles
├── PyPI                            # PyPI packages provided by CSIT
│   ├── jumpavg
│   └── MLRsearch
├── resources
│   ├── api                         # API coverage
│   ├── job_specs                   # Test selection for jenkins job execution
│   ├── model_schema                # Test results model schema
│   ├── templates                   # Templates (vpp_api_test, kubernetes, ...)
│   ├── test_data                   # Robot Test configuration
│   ├── tools
│   │   └── papi                    # PAPI driver
│   ├── topology_schemas
└── topologies                      # Linux Foundation topology files
    ├── available
    └── enabled
```

### CSIT Interactive Dashboard

[CDash](https://csit.fd.io).

### CSIT Documentation

[CDocs](https://csit.fd.io/cdocs/).
