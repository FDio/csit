# The New Model
Version 0.1.0

#### Content

- [Changelog](#changelog)
- [TODOs](#todos)
- [Note](#note)
- [Overview](#overview)


- [The Model](#the-model)
  - [Components](#components)
    - [SUT Specification](#sut-specification)
    - [Processing Module](#processing-module)
    - [Suite and Test](#suite-and-test)
    - [Test data](#test-data)
    - [PAL](#pal)
    - [PAL Specification](#pal-specification)
    - [Presentation](#presentation)
  - [Procedure](#procedure)


- [Specification of the SUT](#specification-of-the-sut)
  - [Structure](#structure)
  - [Topology](#topology)
    - [Network](#network)
    - [Node](#node)
    - [Termination Point](#termination-point)
    - [Link](#link)
  - [Configuration Data](#configuration-data)
  - [SUT Operational Data](#sut-operational-data)


- [Unified Test Interface](#unified-test-interface)
  - [Data structure](#data-structure)
    - [Top Level Sections](#top-level-sections)
    - [Metadata](#metadata)
    - [Data](#data)
      - [Configuration Data](#configuration-data)
      - [Results](#results)
      - [Operational Data](#operational-data)
  - [Chain of Changes](#chain-of-changes)
  - [Unified Test Interface Lifecycle](#unified-test-interface-lifecycle)
    - [Initialisation](#initialisation)
    - [Data Collection](#data-collection)
    - [Providing the Collected Data](#providing-the-collected-data)
 
 
- [Implementation](#implementation)
  - [Design](#design)
  - [Tools and Libraries](#tools-and-libraries)

#### Changelog

| Version  | Changes                                                          |
|----------|------------------------------------------------------------------|
| 0.1.0    | Initial revision                                                 |

#### TODOs

1. Create an example of the 
   [topology model](topology_model.json "topology_model.json").
1. Describe the topology here: 
   [Specification of the SUT](#specification-of-the-sut)
1. Change [unified test interface](unified_test_interface.json) to reflect last
   changes.
1. Describe them here: [Unified Test Interface](#unified-test-interface)
1. Add implementation details here: [Implementation](#implementation)

#### Note

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119
"Key Words for use in RFCs to Indicate Requirement Levels").

#### Overview

This document describes the new model of configuring and running tests / suites
and collecting the operational data and results produced by them.
The first chapter [The Model](#the-model) briefly describes the model itself.
Then it deals with [Specification of the SUT](#specification-of-the-sut)
as a JSON structure which is a full and the only description of the SUT
and its implementation as a directed graphs with self loops and parallel edges;
and the [Unified Test Interface](#unified-test-interface) which is the only
configuration (if used as an input), and the only output of a test.

# The Model

![The new architecture](pics/overview.svg "The new architecture")

## Components

Components stored in the repository:
- [SUT Specification](#sut-specification)
- [PAL Specification](#pal-specification)

Components running in RAM and keeping all data in RAM during runtime:
- [Processing Module](#processing-module),
- [PAL](#pal)

Component running on a testbed by CI/CD:
- [Suite and Test](#suite-and-test)

Components stored in a data storage:
- [Test data](#test-data),
- [Presentation](#presentation)

### SUT Specification

SUT specification is a JSON file
([example](topology_model.json "topology_model.json")) containing the full
information about the system under test. It includes mainly:

- topology
- configuration of all nodes and links to be configured before tests

For more information see the section
[Specification of the SUT](#specification-of-the-sut).

### Processing Module

When a test starts, an instance of the processing module is created. It reads
the SUT specification and creates a model of the tested network topology.
Then it passes the configuration information to the test.

While the test runs, it continuously collects operational data and passes it
to the processing module together with the results. All collected information
is preserved even the test fails in a fatal way.

At the end, the data is transformed to JSON format and sent to the storage
by CI/CD tool.

### Suite and Test

> TODO: Decide if it will operate on a suite or test level.

Test running on a test bed configured by the processing module with data from
SUT Specification and providing all operational data and results back to the
processing module.

### Test data

All information about a test (topology, test bed configuration, DUT
configuration, operational data, results, ...) stored in a database.

### PAL

Presentation and Analytics Layer (PAL) makes possible to present and
analyse the test results generated by CSIT Jenkins jobs.

### PAL Specification

PAL specification is a YAML file
([example](../../resources/tools/presentation/specification.yaml)) which
specifies all elements to generate by PAL.

It is not necessary to modify the current version, but there is a place for
optimization.

### Presentation

The presentation includes all elements generated by PAL and published.

## Procedure

1. Create the instance of "Test Data Processing".
1. Read the specification of the suite / test.
1. Configure the suite / test.
1. Run the suite / test.
1. Collect data while running the test. If running a suite, collect data
   separately for each test.
1. Collect the results from the test. If running a suite, collect results
   separately for each test.
1. Save suite / test data locally. Save all collected data and results even
   the test / suite / build fails.
1. Upload all data to the storage. 

# Specification of the SUT

> TODO: Add more precise information

See an example SUT specification [here](topology_model.json).

## Structure

The JSON file includes following information:

- [Topology](#topology) - Provides information about all nodes in topology
  and their interconnection.
- [Configuration Data](#configuration-data) - Configuration of all elements in
  the topology.
- [SUT Operational Data](#sut-operational-data) - Placeholder for operational
  data collected while the test is running.

## Topology

The topology is described as a network by nodes with termination points and
links between them. Each element in this model has attributes, some of them
have configuration data. See below.

```json
{
  "version": "0.1.0",
  "metadata": {...},
  "reference": {...},
  "network": {
    "network-id": "str",
    "node": [...],
    "link": [...]
  }
}
```

**version** 
Version of the specification. Versioned is the structure of the specification
not data in it. This key MUST be present in the specification and its name
MUST NOT be changed. Its value MUST be changed after each update of the
structure. It consists of three parts separated by a comma: MAJOR.MINOR.PATCH.
Increment the:
  - MAJOR version when the changes are incompatible with the previous version,
  - MINOR version when the changes are backwards compatible with the previous
    version, and
  - PATCH version when the changes are backwards compatible bug fixes.
The version of the data specification, and the version of this document MUST be
the same.

**metadata**


**reference**


**network**



### Network

```json
{
  ...
  "network": {
    "network-id": "str",
    "node": [...],
    "link": [...]
  }
}
```

**network-id**


**node**


**link**


### Node

```json
{

  ...

  "network": {
    ...
    
    "node": [
      {
        "node-id": "str",
        "attr": {},
        "configuration": {},
        "operational-data": {},
        "termination-point": [...]
      }
    ],

    ...

  }
}
```

**node-id**


**attr**


**configuration**


**operational-data**


**termination-point**


### Termination Point

```json
{

  ...

  "network": {

    ...

    "node": [
      {

        ...

        "termination-point": [
          {
            "tp-id": "str",
            "attr": {}
          },
          {...}
        ]
      }
    ],

    ...

  }
}
```

**tp-id**


**attr**


### Link

```json
{

  ...

  "network": {

    ...

    "link": [
      {
        "link-id": "str",
        "attr": {},
        "source": {
          "source-node": "node-id",
          "source-tp": "tp-id"
        },
        "destination": {
          "destination-node": "node-id",
          "destination-tp": "tp-id"
        }
      },
      {...}
    ]
  }
}
```

**link-id**


**attr**


**source**


**destination**


## Configuration Data

TODO

## Operational Data

TODO

# Unified Test Interface

TODO: Rewrite

The described JSON data structure is a single source of output data from a
test. The data included in it is collected during the setup and testing phases
of each test. At the end a dedicated RF keyword prints created JSON structure
as a human-readable string into the output.xml file, level info. It is not
necessary to print it as the test message. The information can be then parsed
out processed by PAL.

## Data Structure

### Top Level Sections

For detailed information see the [example](unified_test_interface.json).

- **data_structure_version** - This key MUST be present in the structure and
  its name MUST NOT be changed. Its value MUST be changed after each update of
  the structure. It consists of three parts separated by a comma:
  MAJOR.MINOR.PATCH. Increment the:
  - MAJOR version when the changes are incompatible with the previous version,
  - MINOR version when the changes are backwards compatible with the previous
    version, and
  - PATCH version when the changes are backwards compatible bug fixes.
  The version of the data structure, and the version of this document MUST be
  the same.
- **metadata** - This key SHOULD be present in the structure and its name 
  SHOULD NOT be changed. If there are any changes in this section, the
  `data_structure_version` MUST be increased.
- **data** - This key SHOULD be present in the structure and its name SHOULD
  NOT be changed. If there are any changes in this section, the
  `data_structure_version` MUST be increased.

### Metadata

This section includes data about:

- **test_executor** - The name of executor (e.g. Jenkins) and its base
  parameters e.g. job name and build number.
- **test_execution** - Parameters of test execution itself, e.g. status.
- **system_under_test** - Properties of the system under test.
- **test** - Test parameters, e.g. test ID, tags, documentation, ...

### Data

- **configuration** - Configuration of all nodes in the tested topology. The
  nodes can be TGs, DUTs, VMs, containers, ... and information included in this
  field depends on the type of node. It is described in the section
  **[Configuration](#configuration)**.
- **results** - Results of the test. Their structure depends on the test type.
  It is described in the section **[Results](#results)**.
- **operational_data** - [Operational data](#sut-operational-data) collected on
  the nodes. In this version it includes only output from `show runtime`
  command.


time series data


#### Configuration

TODO

#### Results

TODO

#### SUT Operational Data

TODO

## Chain of Changes

TODO

## Unified Test Interface Lifecycle

TODO

### Initialisation

TODO

### Data collection

TODO

### Providing the collected data

TODO

# Implementation

TODO

## Design

TODO

## Tools and Libraries

TODO

[NetworkX](https://networkx.org/documentation/stable/index.html
"NetworkX - Network Analysis in Python")
