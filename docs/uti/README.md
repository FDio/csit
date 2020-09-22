
Version 0.1.0

#### Content

<!-- MarkdownTOC autolink="true" -->

- [Note](#note)
- [Overview](#overview)
- [Representation of the System under Test](#representation-of-the-system-under-test)
  - [Structure](#structure)
  - [Topology](#topology)
    - [Network](#network)
    - [Node](#node)
    - [Termination Point](#termination-point)
    - [Link](#link)
  - [Configuration Data](#configuration-data)
  - [Operational Data](#operational-data)
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

#### Note

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119
"Key words for use in RFCs to Indicate Requirement Levels").

#### Overview

TODO

# Representation of the System under Test

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

For detailed information see the`data_structure.json` file.

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
  **Configurations**.
- **results** - Results of the test. Their structure depends on the test type.
  It is described in the section **Results**.
- **operational_data** - Operational data collected on the nodes. In this
  version it includes only output from `show runtime` command.


time series data


#### Configuration

TODO

#### Results

TODO

#### Operational Data

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
