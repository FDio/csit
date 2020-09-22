
Version 0.1.0

#### Content

<!-- MarkdownTOC autolink="true" -->

- [History](#history)
- [Note](#note)
- [Overview](#overview)
- [Representation of the SUT](#representation-of-the-sut)
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
  - [Tools](#Tools)

<!-- /MarkdownTOC -->

#### History

| Version  | Changes                                                          |
|----------|------------------------------------------------------------------|
| 0.1.0    | Initial revision                                                 |


#### Note

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119
"Key words for use in RFCs to Indicate Requirement Levels").

#### Overview

This document describes the
[Representation of the SUT](#representation-of-the-sut)
as a JSON structure which is a full and the only description of the SUT
and its implementation as a directed graphs with self loops and parallel edges;
and the [Unified Test Interface](#unified-test-interface) which is the only
configuration (if used as an input) and the only output of a test.

# Representation of the SUT

TODO

## Structure

TODO

## Topology

TODO

### Network

TODO

### Node

TODO

### Termination Point

TODO

### Link

TODO

## Configuration Data

TODO

## Operational Data

TODO

# Unified Test Interface

The described JSON data structure is a single source of output data from a
test. The data included in it is collected during the setup and testing phases
of each test. At the and a dedicated RF keyword prints created JSON structure
as a human readable string into the output.xml file, level info. It is not
necessary to print it as the test message. The information can be then parsed
out processed by PAL.

## Data Structure

### Top Level Sections

For detailed information see the [example](unified_test_interface.json).

- **data_structure_version** - This key MUST be present in the structure and
  its name MUST NOT be changed. Its value MUST be changed after each update of
  the structure. It consists of three parts separated by a comma:
  MAJOR.MINOR.PATCH. Increment the:
  - MAJOR version when the changes are incompatible with previous version,
  - MINOR version when the changes are backwards compatible with previous
    version, and
  - PATCH version when the changes are backwards compatible bug fixes.
  The version of the data structure and the version of this document MUST be
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
- **operational_data** - [Operational data](#sut-operational-data) collected on the nodes. In this
  version it includes only output from `show runtime` command.


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

## Tools

TODO

[NetworkX](https://networkx.org/documentation/stable/index.html
"NetworkX - Network Analysis in Python")
