================================
 Envisioning information by PAL
================================

Introduction
------------

This document describes possible improvements in data presentation provided by
PAL for the `Report <https://docs.fd.io/csit/master/report/>`_ and the
`Trending <https://docs.fd.io/csit/master/trending/>`_

You can generate a standalone html version of this document using e.g.
rst2html5 tool:

.. code:: bash

    rst2html5 --stylesheet graphs_improvements.css graphs_improvements.rst >> graphs_improvements.html

**Modifications of existing graphs**

- `Speedup Multi-core`_
- `Packet Throughput`_
- `Packet Latency`_
- `HTTP-TCP Performance`_

**New graphs to be added**

- `Comparison between releases`_
- `Comparison between processor architectures`_
- `Comparison between 2-node and 3-node topologies`_
- `Comparison between different physical testbed instances`_
- `Comparison between NICs`_
- `Other comparisons`_

**Export of static images**

- low priority
- make possible to `export static images`_ which are available via link on the
  web page.
- vector formats (svg, pdf) are preferred

Priorities
----------

**Target CSIT-18.10**

- `Speedup Multi-core`_
- `Packet Throughput`_

**Nice to have in CSIT-18.10**

.. note::

    Only if above done, and target CSIT-18.10 is in time , otherwise next
    release.

- `Packet Latency`_
- `HTTP-TCP Performance`_

Modifications of existing graphs
--------------------------------

The proposed modifications include the changes in:

- the layout of the graphs,
- the data and way how it is presented,
- the test cases presented in the graphs.

The first two points are described below, the last one will be added later as a
separate chapter.

.. TODO: [TF], [MK]: Review the TCs displayed in the graphs.

.. _Speedup Multi-core:

Speedup Multi-core
``````````````````

The "Speedup Multicore" graph will display the measured data together with
ideal values calculated as multiples of the value measured using one core.
The difference between measured and ideal values will be displayed in the
label next to each data point.

.. image:: pic/graph_speedup.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Speedup Multi-core: not found.

.. note::

    The svg is not perfect so here is the link to the `xlsx <TODO>`_
    version of the graph.

**Description:**

*Data displayed:*

- one or more data series from the same area, keep the number of displayed
  data series as low as possible (max 5)
- x-axis: number of cores
- y-axis: throughput (measured and ideal) [Mpps], linear scale, beginning with 0
- data point labes: relative difference between measured and ideal values [%]
- hover information: Throughput, Speedup, Diff

*Layout:*

- plot type: lines with data points
- data series format:
    - measured: solid line with data points
    - ideal: dashed line with data points, the same color as "measured"
- title: "Packet throughput Rate Speedup: <area, scaling, features, ...>",
  top, centered, font size 16
- x-axis: integers, starting with 0, linear, font size 14, bottom
- x-axis label: "[Nr of cores]", right
- y-axis: integers, starting with 0, linear, font size 14, left
- y-axis label: "[Mpps]", top, left
- legend: "Measured <area, scaling, features, ...>", "Ideal <area,
  scaling, features, ...>" for each data series, bottom, centered, font size 14

.. _Packet Throughput:

Packet Throughput
`````````````````

The "Packet Throughput" graph will display the measured data using
statistical box graph. Each data point is constructed from 10 samples.
The statistical data are displayed as hover information.

.. image:: pic/graph_throughput.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Packet Throughput" not found.

.. note::

    The svg is not perfect so here is the link to the `xlsx <TODO>`_
    version of the graph.

**Description:**

*Data displayed:*

- one or more data points from the same area, keep the number of displayed
  data points as low as possible (max 10)
- x-axis: indexed testcases
- y-axis: throughput [Mpps], logarithmic scale,
  beginning with 0
- hover information: statistical data (min, lower fence, q1, median, q3,
  higher fence, max), test case name

*Layout:*

- plot type: statistical box
- data series format: box
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: integers, starting with 1, linear, font size 14, bottom
- x-axis label: "[Indexed Test Cases]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Indexed test cases", bottom, centered, font size 14

.. _Packet Latency:

Packet Latency
``````````````

The "Packet Latency" graph will display the measured data using
statistical box graph. Each data point is constructed from 10 samples.
The statistical data are displayed as hover information.

.. image:: pic/graph_latency.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Packet Latency" not found.

.. note::

    The svg is not perfect so here is the link to the `xlsx <TODO>`_
    version of the graph..

**Description:**

*Data displayed:*

- one or more data points from the same area, keep the number of displayed
  data points as low as possible (max 10)
- x-axis: data flow directions
- y-axis: latency min/avg/max [uSec], linear scale, beginning with 0
- hover information: statistical data (min, lower fence, q1, median, q3,
  higher fence, max), test case name

*Layout:*

- plot type: statistical box
- data series format: box
- title: "Latency: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: text, font size 14, bottom
- x-axis label: "[Indexed Test Cases]", right
- y-axis: integers, starting with 0, linear, font size 14, left
- y-axis label: "Latency min/avg/max [uSec]", top, left
- legend: "Indexed test cases", bottom, centered, font size 14

.. _HTTP-TCP Performance:

HTTP/TCP Performance
````````````````````

The "HTTP/TCP Performance" graph will display the measured data using
statistical box graph separately for "Connections per second" and "Requests per
second". Each data point is constructed from 10 samples. The statistical data
are displayed as hover information.

.. image:: pic/graph_http.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "HTTP/TCP Performance" not found.

.. note::

    The svg is not perfect so here is the link to the `xlsx <TODO>`_
    version of the graph.

**Description:**

*Data displayed:*

- requests/connections per second, the same tests configured for 1, 2 and
  4 cores (3 data points in each graph)
- x-axis: indexed test cases
- y-axis: requests/connections per second, linear scale, beginning with 0
- hover information: statistical data (min, lower fence, q1, median, q3,
  higher fence, max), test case name

*Layout:*

- plot type: statistical box
- data series format: box
- title: "VPP HTTP Server performance", top, centered, font size 16
- x-axis: integers, font size 14, bottom
- x-axis label: "[Indexed Test Cases]", right
- y-axis: floats, starting with 0, linear, font size 14, left
- y-axis label: "Connections per second [cps]", "Requests per second [rps]",
  top, left
- legend: "Indexed test cases", bottom, centered, font size 14

New graphs to be added
----------------------

- *Comparison between releases*

    - compare MRR, NDR, PDR between releases
    - use as many releases as available

- *Comparison between processor architectures*

    - compare MRR, NDR, PDR between processor architectures
    - HSW vs SKX (vs ARM when available)

- *Comparison between 2-node and 3-node topologies*

    - compare MRR, NDR, PDR between topologies
    - 3n-skx vs 2n-skx

- *Comparison between different physical testbed instances*

    - compare the results of the same test (MRR, NDR, PDR) run on different
      instances of the same testbed, e.g. HSW
    - HSW vs HSW, SKX vs SKX

- *Comparison between NICs*

    - compare the results of the same test (MRR, NDR, PDR) run on different NICs
      but on the same instance of a physical testbed.
    - x520 vs x710 vs xl710 on HSW
    - x710 vs xxv710 on SKX

- *Other comparisons*

.. note::

    - Partially based on the existing tables in the Report
    - Only selected TCs

.. _Comparison between releases:

Comparison between releases
```````````````````````````

This graph will compare the results of the same test from different releases.
One graph can present the data from one or more tests logically grouped. See
`Grouping of tests in graphs`_ for more information.
Each data point is constructed from 10 samples. The statistical data are
displayed as hover information.

.. image:: pic/graph_cmp_releases.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Comparison between releases" not found.

**Description:**

*Data displayed:*

- data: packet throughput
- x-axis: release
- y-axis: throughput [Mpps], logarithmic scale, beginning with 0
- hover information: statistical data (median, stdev), test case name, release

*Layout:*

- plot type: scatter with line
- data series format: line with markers
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: strings, font size 14, bottom
- x-axis label: "[Release]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Test cases", bottom, centered, font size 14

.. _Comparison between processor architectures:

Comparison between processor architectures
``````````````````````````````````````````

This graph will compare the results of the same test from the same release run
on the different processor architectures (HSW, SKX, later ARM).
One graph can present the data from one or more tests logically grouped. See
`Grouping of tests in graphs`_ for more information.
Each data point is constructed from 10 samples. The statistical data are
displayed as hover information.

.. image:: pic/graph_cmp_arch.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Comparison between processor architectures" not found.

**Description:**

*Data displayed:*

- data: packet throughput
- x-axis: processor architecture
- y-axis: throughput [Mpps], logarithmic scale, beginning with 0
- hover information: statistical data (median, stdev), test case name, processor
  architecture

*Layout:*

- plot type: scatter with line
- data series format: line with markers
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: strings, font size 14, bottom
- x-axis label: "[Processor architecture]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Test cases", bottom, centered, font size 14

.. _Comparison between 2-node and 3-node topologies:

Comparison between 2-node and 3-node topologies
```````````````````````````````````````````````

This graph will compare the results of the same test from the same release run
on the same processor architecture but different topologies (3n-skx, 2n-skx).
One graph can present the data from one or more tests logically grouped. See
`Grouping of tests in graphs`_ for more information.
Each data point is constructed from 10 samples. The statistical data are
displayed as hover information.

.. image:: pic/graph_cmp_topo.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Comparison between 2-node and 3-node topologies" not found.

**Description:**

*Data displayed:*

- data: packet throughput
- x-axis: topology
- y-axis: throughput [Mpps], logarithmic scale, beginning with 0
- hover information: statistical data (median, stdev), test case name, topology

*Layout:*

- plot type: scatter with line
- data series format: line with markers
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: strings, font size 14, bottom
- x-axis label: "[Topology]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Test cases", bottom, centered, font size 14

.. _Comparison between different physical testbed instances:

Comparison between different physical testbed instances
```````````````````````````````````````````````````````

This graph will compare the results of the same test from the same release run
on the same processor architecture, the same topology but different physical
testbed instances.
One graph can present the data from one or more tests logically grouped. See
`Grouping of tests in graphs`_ for more information.
Each data point is constructed from 10 samples. The statistical data are
displayed as hover information.


.. image:: pic/graph_cmp_testbed.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Comparison between different physical testbed instances" not
          found.

**Description:**

*Data displayed:*

- data: packet throughput
- x-axis: physical testbed instances
- y-axis: throughput [Mpps], logarithmic scale, beginning with 0
- hover information: statistical data (median, stdev), test case name, physical
  testbed instance

*Layout:*

- plot type: scatter with line
- data series format: line with markers
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: strings, font size 14, bottom
- x-axis label: "[Physical testbed instance]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Test cases", bottom, centered, font size 14

.. _Comparison between NICs:

Comparison between NICs
```````````````````````

This graph will compare the results of the same test from the same release run
on the same processor architecture, the same topology but different NICs.
One graph can present the data from one or more tests logically grouped. See
`Grouping of tests in graphs`_ for more information.
Each data point is constructed from 10 samples. The statistical data are
displayed as hover information.

.. image:: pic/graph_cmp_nics.svg
    :width: 800 px
    :scale: 50 %
    :align: center
    :alt: Graph "Comparison between NICs" not found.

**Description:**

*Data displayed:*

- data: packet throughput
- x-axis: NICs
- y-axis: throughput [Mpps], logarithmic scale, beginning with 0
- hover information: statistical data (median, stdev), test case name, NIC

*Layout:*

- plot type: scatter with line
- data series format: line with markers
- title: "Throughput: <area, scaling, features, framesize, cores, ...>",
  top, centered, font size 16
- x-axis: strings, font size 14, bottom
- x-axis label: "[NICs]", right
- y-axis: integers, starting with 0, logarithmic, font size 14, left
- y-axis label: "Throughput [Mpps]", top, left
- legend: "Test cases", bottom, centered, font size 14

.. _Other comparisons:

Other comparisons
`````````````````

**Other tests results comparisons**

- compare packet throughput for vhost vs memif

**Other views on collected data**

- per `Vratko Polak email on csit-dev <https://lists.fd.io/g/csit-dev/message/3008>`_.

.. _Grouping of tests in graphs:

Grouping of tests in graphs
---------------------------

A graph can present results of one or more tests. The tests are grouped
according to the defined criteria. In the ideal case, all graphs use the same
groups of tests.

The grouping of tests is described in a separate document.

.. TODO: [MK], [TF]: Create the document.
.. TODO: [TF]: Add the link.
.. TODO: [TF]: Remove/edit the next paragraph when the document is ready.

**Example of data grouping:**

- ip4: ip4base, ip4scale20k, ip4scale200k, ip4scale2m
    - data presented in this order from left to right
- ip6: similar to ip4
- l2bd: similar to ip4.

.. _Sorting of tests presented in a graph:

Sorting of tests presented in a graph
-------------------------------------

.. TODO: [TF]: How? Key? Specification?

.. _export static images:

Export of static images
-----------------------

..
    [TF] My notes, ignore:

    - https://plot.ly/python/static-image-export/
    - prefered vector formats (svg, pdf)
    - requirements:
        - plotly-orca
            - https://github.com/plotly/orca
            - https://github.com/plotly/orca/releases
            - https://plot.ly/python/orca-management/
        - psutil
