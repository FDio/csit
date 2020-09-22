-------------------------------------------------------------------------------
# CSIT-2.0

Version 0.1.0

-------------------------------------------------------------------------------

### Content

- [CSIT-2.0](#csit-20)
    + [Content](#content)
    + [Changelog](#changelog)
    + [Note](#note)
    + [Overview](#overview)
- [The Model](#the-model)
  * [Components](#components)
    + [SUT Specification](#sut-specification)
    + [Processing Module](#processing-module)
    + [Test Bed and Test](#test-bed-and-test)
    + [Test Data](#test-data)
    + [PAL](#pal)
    + [PAL Specification](#pal-specification)
    + [Presentation](#presentation)
  * [Procedure](#procedure)
- [Test Definition](#test-definition)
  * [Files Defining the Test](#files-defining-the-test)
  * [Suite and Test Definition](#suite-and-test-definition)
    + [Version](#version)
    + [Metadata](#metadata)
    + [Resource](#resource)
    + [Network](#network)
      - [Node](#node)
      - [Link](#link)
    + [Suite](#suite)
    + [Test](#test)
- [Unified Test Interface](#unified-test-interface)
  * [Top-level Structure](#top-level-structure)
  * [Log](#log)
    + [Log Item Examples](#log-item-examples)
  * [Test Results](#test-results)
    + [Results](#results)
      - [The Structure of Results](#the-structure-of-results)
        * [NRDPDR PPS Test](#nrdpdr-pps-test)
        * [NRDPDR CPS Test](#nrdpdr-cps-test)
        * [MRR Test](#mrr-test)
        * [Soak Test](#soak-test)
        * [Reconfiguration Test](#reconfiguration-test)
        * [Hoststack Test](#hoststack-test)
        * [Device Test](#device-test)
  * [Examples](#examples)
  * [Unified Test Interface Lifecycle](#unified-test-interface-lifecycle)
    + [Initialisation](#initialisation)
    + [Data Collection](#data-collection)
    + [Providing the Collected Data](#providing-the-collected-data)
- [Implementation](#implementation)
  * [Building the Suite Definition](#building-the-suite-definition)

### Changelog

| Version  | Changes                                                          |
|----------|------------------------------------------------------------------|
| 0.1.0    | Initial revision                                                 |

### Note

The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119
"Key Words for use in RFCs to Indicate Requirement Levels").

### Overview

This document describes the new design of configuring and running tests
and collecting the operational data and results produced by them. It deals with

- the [The Model](#the-model) - brief description of the model itself.
- the [Test Definition](#test-definition) as a set of definition files which is
  a full and the only description of the SUT and test itself;
- the [Unified Test Interface](#unified-test-interface) which is the only
  output of a test (results, operational data, counters).
- the [Implementation](#implementation)

-------------------------------------------------------------------------------

# The Model

![The new architecture](pics/overview.svg "The new architecture")

## Components

Components stored in the repository:
- [SUT Specification](#sut-specification)
- [PAL Specification](#pal-specification)

Components running in RAM and keeping all data in RAM during the runtime:
- [Processing Module](#processing-module),
- [PAL](#pal)

Component running on a testbed by CI/CD:
- [Test Bed and Test](#test-bed-and-test)

Components stored in a data storage:
- [Test Data](#test-data),
- [Presentation](#presentation)

### SUT Specification

SUT specification is a set of files ([example](examples/input_test_definition))
containing the full information about the system under test. It includes mainly
information about:

- resources,
- topology,
- configuration,
- suite and test specification.

For more information see the section
[Test Definition](#test-definition).

### Processing Module

When a test starts, an instance of the processing module is created. It reads
the SUT specification and creates a model of the tested network topology.
Then it passes the configuration information to the test.

While the test runs, it continuously collects operational data and passes it
to the processing module together with the results. All collected information
is preserved even the test fails in a fatal way.

At the end, the data is transformed to the JSON format and sent to the storage
by CI/CD tool.

### Test Bed and Test

Test running on a test bed created and configured by the processing module with
data from SUT Specification and providing all operational data and results back
to the processing module.

### Test Data

All information about a test (topology, test bed configuration, DUT
configuration, operational data, results, ...) stored in a database.

### PAL

Presentation and Analytics Layer (PAL) makes possible to present and
analyse the test results generated by CSIT Jenkins jobs.

### PAL Specification

PAL specification is a set of YAML files
([example](../../resources/tools/presentation/specifications/report) which
specifies all elements to generate by PAL.

It is not necessary to modify the current version, but there is a place for
optimization.

### Presentation

The presentation includes all elements generated by PAL and published.

## Procedure

1. Create the instance of "Test Data Processing" module.
1. Read the specification of the test bed and test.
1. Create the test bed and configure it.
1. Configure the test.
1. Run the test.
1. Collect data while running the test. The data must be collected separately
   for each test.
1. Collect the results from the test. The results must be collected separately
   for each test.
1. Save the test data locally. Save all collected data and results even
   the test / suite / build fails.
1. Upload all data to the storage.

-------------------------------------------------------------------------------

# Test Definition

We will distinguish these phases of suite and test life cycle:

- suite setup,
- test setup,
- test configuration,
- measurement (e.g. find MRR),
- verification of results,
- test teardown,
- suite teardown.

The measurement phase can include also re-configuration.

The **test definition** or topology model is considered to be an
**input information**. It includes all information to
- allocate resources,
- build the topology,
- configure all elements in the topology and
- perform the test.

The test definition is composed of:

1. topology specification,
1. specification common for all tests in a suite, and
1. test specification.

The suite (test) definition consists of two parts:

1. **Static**, pre-defined parameters stored in gerrit, and
1. **Dynamic** parameters which values are added when the execution stats.
   Dynamic properties are:
   - test type
   - test bed
     - topology
     - architecture
     - topology file
     - NICs
     - number of cores and threads
   - resources

See an example [here](examples/input_test_definition)

## Files Defining the Test

The proposed directory and file structure:

```text
topology/
 - topology files (yaml)
suites/
 - suite definitions (json)
```

Topology files define the testbeds, their nodes and NICs. The current set of
the topology files is [here](../../topologies/available).
Topology file is a dynamic parameter set when a test bed is reserved.

Suite definition files define the test suites and tests in them.

## Suite and Test Definition

The suite and test definition is a JSON file which includes the information
about the resources, network, its nodes and links. It specifies its setup and
configuration and collects its states and operational data.

The topology is described as a network by nodes with termination points and
links between them. Each element in this model has attributes, some of them
have configuration data. See below.

See the [model](suite_specification.json) and an
[example](examples/input_test_definition/suites/2n1l-10ge2p1x710-ethip4-ip4base-ndrpdr.json)

```json
{
  "version": "0.1.0",
  "metadata": {},
  "resource": [],
  "network": [],
  "suite": {},
  "test": []
}
```

### Version

Version of the specification. Versioned is the structure of the specification
not data in it. This key MUST be present in the specification and its name
MUST NOT be changed. Its value MUST be changed after each update of the
structure. It consists of three parts separated by a dot: MAJOR.MINOR.PATCH.
Increment the:
  - MAJOR version when the changes are incompatible with the previous version,
  - MINOR version when the changes are backwards compatible with the previous
    version, and
  - PATCH version when the changes are backwards compatible bug fixes.

The version of the data specification, and the version of this document MUST be
the same.

### Metadata

Key-value pairs defining the metadata of the model. It is a placeholder, not
specified yet.

### Resource

Resource is a list of hardware and virtual resources needed to build the
testbed. There can be listed chassis, processor cores, memory, interfaces,
containers, ..., and their relationship (parent, child).

```json
{

  "resource": [
    {
      "resource_id": "str",
      "resource_type": "str",
      "parent": "str resource-id",
      "attr": {},
      "children": "list of resource-id",
      "configuration": "dict depends on resource-type"
    },
    {}
  ]

}
```

The resources and their structure (parent - children) are close connected
to the topology. This list is created before the execution starts and defines
the resource requirements by setting the values of:

- resource-id,
- resource-type,
- parent,
- children, and
- configuration.

The attributes in `attr` are set when the resource is allocated during the
execution. Also, new resources can be added to the list if they are dynamically
created while the test is running (either as a part of configuration,
re-configuration or the measurement phase).

**resource-id**

Unique ID identifying the resource. The ID is unique within the model.

**resource-type**

The type of the resource, e.g.:
- chassis,
- processor core,
- memory,
- interface, ...

**attr**

Key-value pairs defining the attributes of the resource, e.g. size of memory if
the resource is a RAM.

**parent**

`resource-id` of the parent resource. There can be only one parent for the
resource. If the `parent` is not defined (this key does not exist), the
resource is not a nested resource.

**children**

List of children of the resource. It includes the `resource-id` of all
resources directly nested in this resource. If the `children` is empty, or it
is not defined (this key does not exist), the resource has no nested resources.

**configuration**

A dictionary specifying the pre-configuration of the resource. If the resource
is not configurable, this key does not exist.

### Network

A network is defined by [nodes](#node) with termination points connected by
[links](#link).

```json
{

  "network": [
    {
      "network_id": "str",
      "attr": {
        "nodes": "int",
        "topology": "str relative or full path"
      },
      "node": [],
      "link": []
    },
    {}
  ]

}
```

The item `network` in the model is a list as there can be more than one
network specified. They CAN be multiple logical network topologies that are or
are not interconnected.

**network-id**

Unique ID identifying the network. The ID is unique within the model.

**attr**

Key-value pairs defining the attributes of the network.

- *nodes* - number of nodes in the topology.
- *topology* - the file defining the topology of the test bed - dynamic
  parameter set when the test bed is reserved.

**node**

List of nodes in the network, see [Node](#node).

**link**

List of links connecting the nodes, see [Link](#link).

#### Node

A node in the network CAN be software providing a network function (e.g. VPP)
or a container, VM, etc.

A node can include zero, one, or more nested nodes. The node with nested
node(s) is the parent, a node nested in another node is its child.

```json
{

  "network": [
    {

      "node": [
        {
          "node_id": "str",
          "node_type": "str TG | DUT | ...",
          "node_topo": "str node ID used in topology file",
          "parent": "str node_id",
          "children": "list of node_ids",
          "resource": "str resource_id or list of resource_id",
          "configuration": {
            "pre_configuration": [],
            "run_time": []
          },
          "termination_point": []
        }
      ]

    }
  ]

}
```

**node-id**

Unique ID identifying a node in the network.

**node-type**

The functional type of the node, e.g.:
- traffic generator,
- DUT, ...

**node-topo**

Node identification used in the topology file. This parameter refers to the
node defined in the topology file.

**parent**

`node-id` of the parent node. There can be only one parent for the node. If the
`parent` is not defined (this key does not exist), or it is an empty string,
the node is not a nested node.

**children**

List of children of the node. It includes the `node-id` of all nodes nested in
this node. If the `children` is empty, or it is not defined (this key does not
exist), the node has no nested nodes.

**resource**

A list of resources used by this node.

**configuration**

Configuration of the node. The structure of this item depends on the
`node-type` of the node. The structure of the configuration MUST be JSON
compatible.

- *pre-configuration* - the configuration used before DUT starts
- *run-time* - the configuration used to configure the DUT while it
  runs, e.g. to configure it for the specific test. If the DUT is reconfigured
  during its run-time, this item is a list with configurations in the correct
  order.

Example of run-time configuration for the `node-type == TG`:
- *traffic-profile* - the path to the traffic profile used for the test. Traffic
  profile depends on the TG used.
- *traffic-specification* - JSON data structure fully describing all parameters
  of the traffic used for the test.

> **NOTE:** The items `traffic-profile` and `traffic-specification` are covered
> in a separate document.
>
> **TODO:** Add a link to the document.

**termination-point**

A termination point is a point belonging to a node which makes possible to
connect nodes by links.

```json
{

        "termination_point": [
          {
            "tp_id": "str",
            "attr": {
              "interface": "str port defined in topo file"
            }
          },
          {}
        ]

}
```

Each termination point MUST have a unique ID and CAN have a set of attributes.

The attribute `interface` is a dynamic parameter. Its value is set when the
topology file is selected after test bed reservation.

#### Link

Nodes are connected to each other by links which begin and end in termination
points.

```json
{
  "network": {

    "link": [
      {
        "link_id": "str",
        "attr": {},
        "end_1": {
          "end_1_node": "node-id",
          "end_1_tp": "tp-id"
        },
        "end_2": {
          "end_2_node": "node-id",
          "end_2_tp": "tp-id"
        }
      },
      {}
    ]

  }
}
```

**link-id**

Unique ID identifying a link in the network.

**attr**

Key-value pairs defining the attributes of the link.

**end-1**

The node and the termination point where the link connected to the node.

**end-2**

The node and the termination point where the link connected to the node.

### Suite

```json
{

  "suite": {
    "suite_id": "str fullname",
    "test_type": "str [NDRPDR | MRR | SOAK | ...]",
    "tags": ["str", "list of suite specific tags"],
    "documentation": "str"
  }

}
```

**suite-id**

*Current state*

The `suite-id` must be structured as it is in the current version of CSIT, so
the test generator is able to create the tests/suites. The final version of
`suite-id` is set by the test generator, so it is a dynamic parameter.

*Proposal to the future*

The `suite-id` is a unique (in the whole database of tests) string assigned to
the suite when it is created the first time and never changed. If it is changed,
it means, the suite/test has been changed.

It will be independent of the full test name. So, if the full name changes
(change of test name, suite name or directory tree), it will be still
identified by this ID. It would be the best solution for the time series
(trending) and comparison tables. However, the suite (or test) generator must
respect it.

**test-type**

The `test-type` specifies what and how MUST be tested. Using this information,
the test generator includes the right testing method into the test. The
`test-type` is known only when the test run starts, so it is a dynamic
parameter.

**tags**

List of suite tags common to all tests in the suite.

**documentation**

Suite documentation.

> NOTE: The documentation must be independent of the test type.


**Example:**

```json
{

  "suite": {
    "suite_id": "tests.vpp.perf.ip4.2n1l-10ge2p1x710-ethip4-ip4base",
    "test_type": "NDRPDR",
    "tags": ["NDRPDR", "2_NODE_SINGLE_LINK_TOPO", "BASE", "DRV_VFIO_PCI", "ETH", "ethip4-ip4base", "..."],
    "documentation": "RFC2544: Pkt throughput IPv4 routing test cases [Top] Network Topologies: TG-DUT1-TG 2-node ..."
  }

}
```

### Test

```json
{

  "test": [
    {
      "parameters": ["str", "list of parameters used in other key-value pairs"],
      "test_id": "str test name with parameters",
      "tags": ["str", "list of test specific tags, parameters can be used"],
      "framesize": ["str", "list of values"],
      "core": ["str", "list of values"]
    },
    {}
  ]

}
```

All parameters are dynamic.

**parameters**

List of parameters (e.g. frame size or number of cores) used to generate tests.
These parameters MUST be defined in this section. See the example below.

**test-id**

Unique ID within the suite. The parameters can be used here, see example below.

**tags**

List of test specific tags. Do not repeat those defined in the suite. The
parameters can be used here, see example below.

**frame size**

List of frame sizes.

**core**

List of numbers of cores.

**Examples:**

Using parameters in this example we will get 12 tests - all combinations of
cores and frame sizes:

```json
{

  "test": [
    {
      "parameters": ["framesize", "core"],
      "test_id": "{framesize}-{core}-ethip4-ip4base",
      "tags": ["{framesize}", "{core}"],
      "framesize": ["64B", "1518B", "9000B", "IMIX"],
      "core": ["1C", "2C", "4C"]
    }
  ]

}
```

Using parameters in this example we will get 6 tests - all frame sizes for 1C
and 64B frame size for 2C and 4C:

```json
{

  "test": [
    {
      "parameters": ["framesize", "core"],
      "test_id": "{framesize}-{core}-ethip4-ip4base",
      "tags": ["{framesize}", "{core}"],
      "framesize": ["64B", "1518B", "9000B", "IMIX"],
      "core": ["1C"]
    },
    {
      "parameters": ["framesize", "core"],
      "test_id": "{framesize}-{core}-ethip4-ip4base",
      "tags": ["{framesize}", "{core}"],
      "framesize": ["64B"],
      "core": ["2C", "4C"]
    }
  ]

}
```

-------------------------------------------------------------------------------

# Unified Test Interface

The described JSON data structure is a single source of output data from a
test. The data included in it is collected during the setup and testing phases
of each test. At the end a dedicated RF keyword prints created JSON structure
as a human-readable string into the output.xml file, level info. It is not
necessary to print it as the test message. The information can be then parsed
out and processed by PAL.

The **unified test interface** is considered to be an
**output information**. It MUST provide all information. It includes the same
information as the [Test Definition](#test-definition) and
- test results,
- operational data,
  - states, the resources, nodes and test went through,
  - run-time data,
  - counters.

See the [UTI Specification](unified_test_interface.json) and
[examples](examples/output_uti).

## Top-level Structure

```json
{
  "version": "0.1.0",
  "ci": "str [jenkins | s5ci | manual]",
  "job": "str",
  "build_number": "int",
  "testbed": "str TG IP",
  "suite_id": "str",
  "suite_doc": "str",
  "sut_type": "vpp",
  "sut_version": "str",
  "test_id": "str fullname",
  "test_type": "str [NDRPDR | MRR | SOAK | ...]",
  "test_doc": "str",
  "tags": ["str", "list of all tags"],
  "start_time": "str datetime",
  "end_time": "str datetime",
  "status": "str [PASS | FAIL]",
  "message": "str",
  "results": {},
  "resource": [],
  "network": [],
  "log": []
}
```

The items

- version,
- resource and
- network

are the same and with the same structure as defined in
[Test Definition](#test-definition).

The other items are filled with data during the runtime of the test.

## Log

The log is a list of items representing all events encountered during the run
of test. This is the only place where this kind of information is stored.

```json
{

  "log": [
    {
      "source_type": "str node | resource | test | ...",
      "source_id": "str node_id | resource_id | test_id | ...",
      "msg_type": "str papi | log | metric | ...",
      "log_level": "str or int NOTSET=0 | DEBUG=10 | INFO=20 | WARNING=30 | ERROR=40 | CRITICAL=50",
      "timestamp": "datetime",
      "msg": "str",
      "data": "list | dict"
    },
    {}
  ]

}
```

**source-[type | id]**

A part of the system where the log item and the data come from.

**msg-type**

A type of the message written to the log:

- command history,
- ...

**log-level**

Possible log levels:

| Level    | Numeric value |
|----------|---------------|
| CRITICAL | 50            |
| ERROR    | 40            |
| WARNING  | 30            |
| INFO     | 20            |
| DEBUG    | 10            |
| NOTSET   | 0             |

**timestamp**

The date and time when the item was written to the log.

**msg**

The text part of the log item, CAN be empty.

**data**

The data part of the log item, CAN be empty.

### Log Item Examples

**papi history**

```json
{
  "log": [
    {
      "source_type": "node",
      "source_id": "dut1",
      "msg_type": "papi",
      "log_level": "INFO",
      "timestamp": "20210203 06:50:13.701",
      "msg": "cli_inband(cmd='show logging')",
      "data": []
    },
    {}
  ]
}
```

**show-runtime**

```json
{

  "log": [
    {
      "source_type": "node",
      "source_id": "dut1",
      "msg_type": "metric",
      "log_level": "INFO",
      "timestamp": "20210128 13:00:51.766",
      "msg": "show-runtime",
      "data": [
        {
            "name": "calls",
            "value": 0,
            "labels": {
                "host": "10.30.51.21",
                "socket": "/run/vpp/stats.sock",
                "graph_node": "dpdk-input",
                "thread_id": "0"
            }
        },
        {
            "name": "calls",
            "value": 313060437,
            "labels": {
                "host": "10.30.51.21",
                "socket": "/run/vpp/stats.sock",
                "graph_node": "dpdk-input",
                "thread_id": "1"
            }
        },
        {}
      ]
    }
  ]

}
```

The item `host` is here only in the first version of the data model used by
the XML to JSON converter. Later, this information will be in the `network`
section.

**metric**

```json
{

    "log": [
      {
        "source_type": "str node | resource | test | ...",
        "source_id": "str node-id | resource-id | test-id | ...",
        "msg_type": "metric",
        "msg": "show-runtime",
        "timestamp": "str datetime",
        "data": [
          {
            "name": "str",
            "labels": {
              "label_1": "str",
              "label_n": "str"
            },
            "value": "str"
          },
          {}
        ]
      },
      {}
    ]

}
```

For telemetry example see
[UTI NDRPDR](examples/output_uti/78b-1t1c-ethip6-ip6base-ndrpdr.json).

## Test Results

```json
{
  "version": "0.1.0",
  "ci": "",
  "job": "",
  "build_number": "",
  "testbed": "",
  "suite_id": "",
  "suite_doc": "",
  "sut_type": "",
  "sut_version": "",
  "test_id": "",
  "test_type": "",
  "test_doc": "",
  "tags": [],
  "start_time": "",
  "end_time": "",
  "status": "",
  "message": "",
  "results": {}
}
```

Here is a list of attributes which are not described in [Test](#test) or are
changed:

**test-id**

The test ID is composed of suite ID and previous test ID with all parameters
replaced by their values.

**tags**

Full list of tags composed of the suite tags, test tags and tags generated
during the execution, e.g. `2T1C`.

**test-doc**

Test documentation.

**message**

Test message.

### Results

Results of the test. Their structure and items present in it, depend on the
test type.

#### The Structure of Results

These examples are taken from real test runs.

##### NRDPDR PPS Test

```json
{

    "results": {
      "throughput": {
        "unit": "pps",
        "ndr": {
          "value": {
            "lower": 33860429.05341475,
            "upper": 34030580.23807432
          },
          "value_gbps": {
            "lower": 22.754208323894712,
            "upper": 22.86854991998594
          }
        },
        "pdr": {
          "value": {
            "lower": 36013017.9117283,
            "upper": 36193986.01615428
          },
          "value_gbps": {
            "lower": 24.200748036681418,
            "upper": 24.32235860285568
          }
        }
      },
      "latency": {
        "forward": {
          "pdr_90": {
            "min": 11.0,
            "avg": 21.0,
            "max": 118.0,
            "hdrh": "HISTFAAAAHx4nJNpmSzMwMCQxQABzFCaEUzOmNZg/wEiIMok9o6phfuK9B7Nd8ZTbL64/Qs8Ef7K54fzEYNLctuE33HdY+1g3sE4g9FCioeFmYWJmYmJm4mVhZWJkYUdyGFkAUI2EGYHsthYgNIsTIxAgoWFkYmNiQOkAqgJhABx9xer"
          },
          "pdr_50": {
            "min": 10.0,
            "avg": 16.0,
            "max": 147.0,
            "hdrh": "HISTFAAAAFN4nJNpmSzMwMBgxAABzFCaEUzOmNZg/wEiINzG9MHtjtOXoGM+R6w3GW2x3uf+QfcX9zzWBrYfog0qWyRfcDxj5GFkYmJlYmRiZLnKyAQAUpAWEA=="
          },
          "pdr_10": {
            "min": 10.0,
            "avg": 19.0,
            "max": 46.0,
            "hdrh": "HISTFAAAAGx4nJNpmSzMwMDgyQABzFCaEUzOmNZg/wEiINznt6duhfsC3R8aHxTuCE3gXcO1g/sZ5xXeHzzXuDZwT+F+JvhN6430BYEF3F0cE1huMU9h28T5g/0S6zKWBpY+ll3Mj5g/MS5gdJICABx5IcE="
          },
          "pdr_0": {
            "min": 10.0,
            "avg": 10.0,
            "max": 43.0,
            "hdrh": "HISTFAAAACx4nJNpmSzMwMDAywABzFCaEUzOmNZg/wEiINxwmKWjhkmeiZ+JnQkAnKcG0A=="
          }
        },
        "reverse": {
          "pdr_90": {
            "min": 10.0,
            "avg": 20.0,
            "max": 122.0,
            "hdrh": "HISTFAAAAHd4nJNpmSzMwMCQxAABzFCaEUzOmNZg/wEiIMwkVPaJeQL/FIVtxidst3mc87sXsMt/k/sG81PqWyQ+8d/iaGK9xbSLMUSJj5GFiZOJkUmYCQjYQYiThZuJFSjCzMIMpMGAhYONiUWAjYuDhYmNhYURJAQAZF4Wsg=="
          },
          "pdr_50": {
            "min": 10.0,
            "avg": 16.0,
            "max": 47.0,
            "hdrh": "HISTFAAAAFB4nJNpmSzMwMBgyAABzFCaEUzOmNZg/wEiILyH5ZTrDo8bKRfCr7mcM9xnfsDmgPokzh8s/1hW8DbInJHcwN7CyMHEwsrExAiEvEwANVAUxg=="
          },
          "pdr_10": {
            "min": 10.0,
            "avg": 19.0,
            "max": 45.0,
            "hdrh": "HISTFAAAAGR4nJNpmSzMwMDgxAABzFCaEUzOmNZg/wEiIPwge5XXN6U+qU9yr8Qfyd0R65H+InVGcorsBrFt0puEF4l9Elok8ELgm9AjoSXcmwQ2sK/h2sfWxfKDqY2xzkmBQ4iNCQBA4h47"
          },
          "pdr_0": {
            "min": 10.0,
            "avg": 10.0,
            "max": 43.0,
            "hdrh": "HISTFAAAACt4nJNpmSzMwMDAwwABzFCaEUzOmNZg/wEiILxoO+sLdlYmfSZmJgCWiQbR"
          }
        }
      }
    }

}
```

##### NRDPDR CPS Test

```json
{

    "results": {
      "throughput": {
        "unit": "cps",
        "ndr": {
          "value": {
            "lower": 1961830.372962205,
            "upper": 1967795.9965891098
          },
          "value_gbps": {
            "lower": -1.0,
            "upper": -1.0
          }
        },
        "pdr": {
          "value": {
            "lower": 1979781.720629949,
            "upper": 1985801.9988565133
          },
          "value_gbps": {
            "lower": -1.0,
            "upper": -1.0
          }
        }
      },
      "latency": {
        "forward": {
          "pdr_90": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_50": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_10": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_0": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          }
        },
        "reverse": {
          "pdr_90": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_50": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_10": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          },
          "pdr_0": {
            "min": -1.0,
            "avg": -1.0,
            "max": -1.0,
            "hdrh": ""
          }
        }
      }
    }

}
```

##### MRR Test

```json
{

    "results": {
      "samples": [
        32898681.325309694,
        33305083.894738417,
        32945683.413171504,
        33285073.667503458,
        33020872.055778056,
        33118601.598959956,
        32267738.309549306,
        32572615.98853764,
        33093353.350239147,
        33165583.88523683
      ],
      "avg": 32967328.7489024,
      "stdev": 307633.54291919054
    }

}
```

##### Soak Test

```json
{

    "results": {
      "critical_rate": {
        "lower": 14879532.196245482,
        "upper": 14981007.507939538
      }
    }

}
```

##### Reconfiguration Test

```json
{

    "results": {
      "loss": 973,
      "time": 0.0003424602634407024
    }

}
```

##### Hoststack Test

```json
{

    "results": {
      "start": 0,
      "end": 20.000044,
      "seconds": 20.000044,
      "bytes": 5687711544,
      "bits_per_second": 2275080000.0,
      "retransmits": 0,
      "omitted": false
    }

}
```

```json
{

    "results": {
      "client": {
        "role": "client",
        "time": "49.246309372",
        "start_evt": "sconnect",
        "start_evt_missing": "False",
        "end_evt": "lastbyte",
        "end_evt_missing": "False",
        "rx_data": 0,
        "tx_data": 10737418240,
        "rx_bits_per_second": 0.0,
        "tx_bits_per_second": 1744279866.2
      },
      "server": {
        "role": "server",
        "time": "49.236072432",
        "start_evt": "sconnect",
        "start_evt_missing": "False",
        "end_evt": "lastbyte",
        "end_evt_missing": "False",
        "rx_data": 10737418240,
        "tx_data": 0,
        "rx_bits_per_second": 1744642528.9,
        "tx_bits_per_second": 0.0
      }
    }

}
```

##### Device Test

```json
{

    "results": {}

}
```

There is only the status (PASS | FAIL).

## Examples

**NDRPDR**

- [UTI NDRPDR](examples/output_uti/78b-1c-ethip6-ip6base-ndrpdr.json)
- [UTI NDRPDR CPS](examples/output_uti/64b-2c-avf-ethip4udp-nat44ed-h4096-p63-s258048-cps-ndrpdr.json)

**MRR**

- [UTI MRR](examples/output_uti/64b-1c-eth-l2patch-mrr.json)

**Soak**

- [UTI Soak](examples/output_uti/64b-1c-ethip4-ip4base-soak.json)

**Hoststack**

- [UTI Hoststack 1](examples/output_uti/1280b-1c-eth-ip4udpquicscale1cl10s-vppecho-bps.json)
- [UTI Hoststack2 ](examples/output_uti/1460b-1c-eth-ip4tcpbase-nsim-ldpreload-iperf3-bps.json)

**Reconfiguration test**

- [UTI Reconfiguration tests](examples/output_uti/64b-1c-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf.json)

**VPP Device Test**

- [UTI VPP Device Test](examples/output_uti/64b-ethipv4-ip4base-dev.json)

## Unified Test Interface Lifecycle

The main principle is: the data is collected continuously, immediately when
the data is generated by any part of the SUT, it is taken, preprocessed and
sent to the object which temporarily stores the data. When the test finishes,
nevertheless if successfully, or it fails, the collected data is stored in the
defined way (a file on the disc, database, ...).

The UTI lifecycle has three main parts:

1. Initialization
1. Data collection
1. Providing the collected data

### Initialisation

The initialization of UTI is the first step in the test lifecycle. An empty,
predefined object with methods to access the data is created. This object
stores the collected data during the test lifecycle. Also, it makes possible to
write, read, modify and delete the data. It is possible to access a single
piece of data or the whole structures.

### Data Collection

The data is stored immediately it is generated. There are robot framework
keywords and python methods to send the data to the python object created in
the initialization phase.

There are two types and many subtypes of data to be collected:

- operational data (stats, counters, metrics)
- results (structure depends on the kind of the test)

Each of the subtype is represented by a class. This class stores a single piece
of structured data (one result, set of statistics, set of metrics, ...).
The class should provide methods to verify collected data and return it in
json format.

All data is stored in an object in the structured way described in this
document. There are methods to:
- add a json structured data on the specified place in the object,
- get the specified data,
- write the data to a json file.

### Providing the Collected Data

The collected data is stored as a json file on the Jenkins executor. One json
file includes data from one test. The json files are gzipped separately. When
all tests are finished, all json files are sent to the storage.

The storage is
[Amazon Simple Storage Service (S3)](https://docs.aws.amazon.com/s3/index.html)
with Amazon S3 Select and S3 Glacier Select support the SELECT SQL command.

The compressed json files are stored in a tree structure following the structure
of jobs builds and suites, e.g.:

```text
_build
├── csit-vpp-device-2101-ubuntu1804-1n-skx
│   └── 358
│       └── tests
│           └── vpp
│               └── device
│                   ├── container memif
│                   │   ├── eth2p-ethipv4-ip4base-eth-2memif-1dcr-dev
│                   │   │   └── 64b-ethipv4-ip4base-eth-2memif-1dcr-dev.json.gz
...
│                   │   │   └── 64b-ethipv4-l2xcbase-eth-2memif-1dcr-dev.json.gz
│                   │   └── eth2p-ethipv6-ip6base-eth-2memif-1dcr-dev
│                   │       └── 78b-ethipv6-ip6base-eth-2memif-1dcr-dev.json.gz
...
│                   ├── stats
│                   │   └── eth2p-ethipv4-l2xcbase-stats-dev
│                   │       └── 64b-ethipv4-l2xcbase-stats-dev.json.gz
│                   └── vm vhost
│                       ├── ip4
│                       │   └── eth2p-ethipv4-ip4base-eth-2vhost-1vm-dev
│                       │       └── 64b-ethip4-ip4base-eth-2vhost-1vm-dev.json.gz
...
│                       └── l2xc
│                           └── eth2p-ethipv4-l2xcbase-eth-2vhost-1vm-dev
│                               └── 64b-ethipv4-l2xcbase-eth-2vhost-1vm-dev.json.gz
└── csit-vpp-perf-report-iterative-2101-3n-hsw
    ├── 65
    │   └── tests
    │       └── vpp
    │           └── perf
    │               └── crypto
    │                   ├── 40ge2p1xl710-ethip4ipsec1000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf
    │                   │   ├── 64b-1t1c-ethip4ipsec1000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf.json.gz
    │                   │   ├── 64b-2t2c-ethip4ipsec1000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf.json.gz
    │                   │   └── 64b-4t4c-ethip4ipsec1000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf.json.gz
...
    │                   └── 40ge2p1xl710-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes256gcm-reconf
    │                       ├── 64b-1t1c-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes256gcm-reconf.json.gz
    │                       ├── 64b-2t2c-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes256gcm-reconf.json.gz
    │                       └── 64b-4t4c-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes256gcm-reconf.json.gz
    └── 69
        └── tests
            └── vpp
                └── perf
                    └── hoststack
                        ├── 40ge2p1xl710-eth-ip4tcpbase-ldpreload-iperf3-bps
                        │   └── 1460b-1t1c-eth-ip4tcpbase-ldpreload-iperf3-bps.json.gz
...
                        ├── 40ge2p1xl710-eth-ip4udpquicscale10cl1s-vppecho-bps
                        │   └── 1280b-1t1c-eth-ip4udpquicscale10cl1s-vppecho-bps.json.gz
                        └── 40ge2p1xl710-eth-ip4udpquicscale1cl10s-vppecho-bps
                            └── 1280b-1t1c-eth-ip4udpquicscale1cl10s-vppecho-bps.json.gz
```

-------------------------------------------------------------------------------

# Implementation

## Building the Suite Definition

The suite definition includes:
- Static parameters which are known when the definition is written. The
  definition is stored in the gerrit only with static parameters as the dynamic
  parameters are not known at this stage.
  > TODO: Should the dynamic parameters be missing from the static definition,
  > or should they have default values? I prefer default values as
  > placeholders.
- Dynamic parameters set when the build stats. They can be set by a user in his
  trigger or by job-spec.
  The dynamic parameters of this kind are e.g.: topology, number of cores,
  frame sizes, NICs, ...
  > TODO: Add complete list.
- Dynamic parameters set by the build itself as they are not known when the
  build starts.
  The dynamic parameters of this kind are e.g.: topology file and all
  parameters specified in it.
