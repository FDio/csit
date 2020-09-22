# Unified Test Interface
Version 0.1.0

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119
"Key words for use in RFCs to Indicate Requirement Levels").

## Overview

The described JSON data structure is a single source of output data from a
test. The data included in it is collected during the setup and testing phases
of each test. At the and a dedicated RF keyword prints created JSON structure
as a human readable string into the output.xml file, level info. It is not
necessary to print it as the test message. The information can be then parsed
out processed by PAL.

## Data structure

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

#### Configurations



#### Results


## Chain of changes



## Unified Test Interface lifecycle


### Initialisation


### Data collection


### Providing the collected data

 

