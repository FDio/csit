
.. _vpp_compare_current_vs_previous_release:

Current vs Previous Release
---------------------------

Relative comparison of VPP packet throughput (NDR, PDR and MRR) between
|vpp-release| and |vpp-release-1| (measured for |csit-release| and
|csit-release-1| respectively) is calculated from results of tests
running on 2-node Intel Xeon Skylake (2n-skx), 3-node Intel Xeon Skylake
(3n-skx), 2-node Intel Atom Denverton
(2n-dnv), 3-node Intel Atom Denverton (3n-dnv), 3-node Arm TaiShan (3n-tsh)
testbeds, in 1-core, 2-core and 4-core (MRR only) configurations.

Listed mean and standard deviation values are computed based on a series
of the same tests executed against respective VPP releases to verify
test results repeatability, with percentage change calculated for mean
values. Note that the standard deviation is quite high for a small
number of packet throughput tests, what indicates poor test results
repeatability and makes the relative change of mean throughput value not
fully representative for these tests. The root causes behind poor
results repeatability vary between the test cases.

.. note::

    Test results are stored in

    - `build logs from FD.io vpp performance job 2n-icx`_,
    - `build logs from FD.io vpp performance job 3n-icx`_,
    - `build logs from FD.io vpp performance job 2n-skx`_,
    - `build logs from FD.io vpp performance job 3n-skx`_,
    - `build logs from FD.io vpp performance job 2n-clx`_,
    - `build logs from FD.io vpp performance job 2n-zn2`_,
    - `build logs from FD.io vpp performance job 2n-dnv`_,
    - `build logs from FD.io vpp performance job 3n-dnv`_,
    - `build logs from FD.io vpp performance job 3n-tsh`_,
    - `build logs from FD.io vpp performance job 2n-tx2`_,
    - `build logs from FD.io vpp performance job 2n-aws`_,

    with RF result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

2n-icx-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-icx-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-icx-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-icx-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-icx-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-icx-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-icx-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-2n-icx-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-icx-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-icx-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-icx-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-icx-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-2n-icx-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-icx-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

3n-icx-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-3n-icx-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-3n-icx-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-3n-icx-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-3n-icx-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-3n-icx-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-3n-icx-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-3n-icx-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-3n-icx-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-3n-icx-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-3n-icx-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-3n-icx-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-3n-icx-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-icx-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

2n-skx-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-skx-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-skx-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-skx-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-skx-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-skx-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-skx-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-2n-skx-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-skx-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-skx-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-2n-skx-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-skx-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

3n-skx-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-3n-skx-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-3n-skx-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-3n-skx-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-3n-skx-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-3n-skx-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-3n-skx-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-3n-skx-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-3n-skx-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-3n-skx-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-3n-skx-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-skx-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

2n-clx-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-clx-xxv710-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-clx-xxv710-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-clx-xxv710-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-clx-xxv710-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-clx-xxv710-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-clx-xxv710-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-2n-clx-xxv710-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-clx-xxv710-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-2n-clx-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-clx-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

2n-clx-cx556a
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-clx-cx556a-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-clx-cx556a-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-clx-cx556a-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-clx-cx556a-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-clx-cx556a-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-clx-cx556a-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-2n-clx-cx556a-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-clx-cx556a-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-2n-clx-cx556a-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-clx-cx556a-2t1c-pdr90-d1-max-csv.csv>`_

2n-zn2-xxv710
~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-zn2-xxv710-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-zn2-xxv710-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-zn2-xxv710-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-zn2-xxv710-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-zn2-xxv710-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-zn2-xxv710-4t2c-mrr.html>`_
  - `HTML 8t4c MRR comparison <performance-changes-2n-zn2-xxv710-8t4c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-mrr.txt>`_
  - `ASCII 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-8t4c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-4t2c-mrr-csv.csv>`_
  - `CSV 8t4c MRR comparison <../../_static/vpp/performance-changes-2n-zn2-xxv710-8t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR50, direction1, average value comparison <latency-changes-2n-zn2-xxv710-2t1c-pdr50-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, average value comparison <latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-avg.html>`_
  - `HTML 2t1c PDR90, direction1, max value comparison <latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-max.html>`_
  - `ASCII 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr50-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-avg.txt>`_
  - `ASCII 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-max.txt>`_
  - `CSV 2t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 2t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-zn2-xxv710-2t1c-pdr90-d1-max-csv.csv>`_

2n-dnv-x553
~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c NDR comparison <performance-changes-2n-dnv-1t1c-ndr.html>`_
  - `HTML 2t2c NDR comparison <performance-changes-2n-dnv-2t2c-ndr.html>`_
  - `ASCII 1t1c NDR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-ndr.txt>`_
  - `ASCII 2t2c NDR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-ndr.txt>`_
  - `CSV 1t1c NDR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-ndr-csv.csv>`_
  - `CSV 2t2c NDR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR comparison <performance-changes-2n-dnv-1t1c-pdr.html>`_
  - `HTML 2t2c PDR comparison <performance-changes-2n-dnv-2t2c-pdr.html>`_
  - `ASCII 1t1c PDR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-pdr.txt>`_
  - `ASCII 2t2c PDR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-pdr.txt>`_
  - `CSV 1t1c PDR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-pdr-csv.csv>`_
  - `CSV 2t2c PDR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c MRR comparison <performance-changes-2n-dnv-1t1c-mrr.html>`_
  - `HTML 2t2c MRR comparison <performance-changes-2n-dnv-2t2c-mrr.html>`_
  - `HTML 4t4c MRR comparison <performance-changes-2n-dnv-4t4c-mrr.html>`_
  - `ASCII 1t1c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-mrr.txt>`_
  - `ASCII 2t2c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-mrr.txt>`_
  - `ASCII 4t4c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-4t4c-mrr.txt>`_
  - `CSV 1t1c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-1t1c-mrr-csv.csv>`_
  - `CSV 2t2c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-2t2c-mrr-csv.csv>`_
  - `CSV 4t4c MRR comparison <../../_static/vpp/performance-changes-2n-dnv-4t4c-mrr-csv.csv>`_

3n-dnv-x553
~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c NDR comparison <performance-changes-3n-dnv-1t1c-ndr.html>`_
  - `HTML 2t2c NDR comparison <performance-changes-3n-dnv-2t2c-ndr.html>`_
  - `ASCII 1t1c NDR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-ndr.txt>`_
  - `ASCII 2t2c NDR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-ndr.txt>`_
  - `CSV 1t1c NDR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-ndr-csv.csv>`_
  - `CSV 2t2c NDR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR comparison <performance-changes-3n-dnv-1t1c-pdr.html>`_
  - `HTML 2t2c PDR comparison <performance-changes-3n-dnv-2t2c-pdr.html>`_
  - `ASCII 1t1c PDR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-pdr.txt>`_
  - `ASCII 2t2c PDR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-pdr.txt>`_
  - `CSV 1t1c PDR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-pdr-csv.csv>`_
  - `CSV 2t2c PDR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c MRR comparison <performance-changes-3n-dnv-1t1c-mrr.html>`_
  - `HTML 2t2c MRR comparison <performance-changes-3n-dnv-2t2c-mrr.html>`_
  - `HTML 4t4c MRR comparison <performance-changes-3n-dnv-4t4c-mrr.html>`_
  - `ASCII 1t1c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-mrr.txt>`_
  - `ASCII 2t2c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-mrr.txt>`_
  - `ASCII 4t4c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-4t4c-mrr.txt>`_
  - `CSV 1t1c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-1t1c-mrr-csv.csv>`_
  - `CSV 2t2c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-2t2c-mrr-csv.csv>`_
  - `CSV 4t4c MRR comparison <../../_static/vpp/performance-changes-3n-dnv-4t4c-mrr-csv.csv>`_

3n-tsh-x520
~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c NDR comparison <performance-changes-3n-tsh-1t1c-ndr.html>`_
  - `HTML 2t2c NDR comparison <performance-changes-3n-tsh-2t2c-ndr.html>`_
  - `ASCII 1t1c NDR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-ndr.txt>`_
  - `ASCII 2t2c NDR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-ndr.txt>`_
  - `CSV 1t1c NDR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-ndr-csv.csv>`_
  - `CSV 2t2c NDR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR comparison <performance-changes-3n-tsh-1t1c-pdr.html>`_
  - `HTML 2t2c PDR comparison <performance-changes-3n-tsh-2t2c-pdr.html>`_
  - `ASCII 1t1c PDR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-pdr.txt>`_
  - `ASCII 2t2c PDR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-pdr.txt>`_
  - `CSV 1t1c PDR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-pdr-csv.csv>`_
  - `CSV 2t2c PDR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c MRR comparison <performance-changes-3n-tsh-1t1c-mrr.html>`_
  - `HTML 2t2c MRR comparison <performance-changes-3n-tsh-2t2c-mrr.html>`_
  - `HTML 4t4c MRR comparison <performance-changes-3n-tsh-4t4c-mrr.html>`_
  - `ASCII 1t1c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-mrr.txt>`_
  - `ASCII 2t2c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-mrr.txt>`_
  - `ASCII 4t4c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-4t4c-mrr.txt>`_
  - `CSV 1t1c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-1t1c-mrr-csv.csv>`_
  - `CSV 2t2c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-2t2c-mrr-csv.csv>`_
  - `CSV 4t4c MRR comparison <../../_static/vpp/performance-changes-3n-tsh-4t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR50, direction1, average value comparison <latency-changes-3n-tsh-x520-1t1c-pdr50-d1-avg.html>`_
  - `HTML 1t1c PDR90, direction1, average value comparison <latency-changes-3n-tsh-x520-1t1c-pdr90-d1-avg.html>`_
  - `HTML 1t1c PDR90, direction1, max value comparison <latency-changes-3n-tsh-x520-1t1c-pdr90-d1-max.html>`_
  - `ASCII 1t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr50-d1-avg.txt>`_
  - `ASCII 1t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr90-d1-avg.txt>`_
  - `ASCII 1t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr90-d1-max.txt>`_
  - `CSV 1t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 1t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 1t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-3n-tsh-x520-1t1c-pdr90-d1-max-csv.csv>`_

2n-tx2-xl710
~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c NDR comparison <performance-changes-2n-tx2-1t1c-ndr.html>`_
  - `HTML 2t2c NDR comparison <performance-changes-2n-tx2-2t2c-ndr.html>`_
  - `ASCII 1t1c NDR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-ndr.txt>`_
  - `ASCII 2t2c NDR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-ndr.txt>`_
  - `CSV 1t1c NDR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-ndr-csv.csv>`_
  - `CSV 2t2c NDR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR comparison <performance-changes-2n-tx2-1t1c-pdr.html>`_
  - `HTML 2t2c PDR comparison <performance-changes-2n-tx2-2t2c-pdr.html>`_
  - `ASCII 1t1c PDR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-pdr.txt>`_
  - `ASCII 2t2c PDR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-pdr.txt>`_
  - `CSV 1t1c PDR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-pdr-csv.csv>`_
  - `CSV 2t2c PDR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c MRR comparison <performance-changes-2n-tx2-1t1c-mrr.html>`_
  - `HTML 2t2c MRR comparison <performance-changes-2n-tx2-2t2c-mrr.html>`_
  - `HTML 4t4c MRR comparison <performance-changes-2n-tx2-4t4c-mrr.html>`_
  - `ASCII 1t1c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-mrr.txt>`_
  - `ASCII 2t2c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-mrr.txt>`_
  - `ASCII 4t4c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-4t4c-mrr.txt>`_
  - `CSV 1t1c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-1t1c-mrr-csv.csv>`_
  - `CSV 2t2c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-2t2c-mrr-csv.csv>`_
  - `CSV 4t4c MRR comparison <../../_static/vpp/performance-changes-2n-tx2-4t4c-mrr-csv.csv>`_

Latency Comparison
``````````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 1t1c PDR50, direction1, average value comparison <latency-changes-2n-tx2-xl710-1t1c-pdr50-d1-avg.html>`_
  - `HTML 1t1c PDR90, direction1, average value comparison <latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-avg.html>`_
  - `HTML 1t1c PDR90, direction1, max value comparison <latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-max.html>`_
  - `ASCII 1t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr50-d1-avg.txt>`_
  - `ASCII 1t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-avg.txt>`_
  - `ASCII 1t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-max.txt>`_
  - `CSV 1t1c PDR50, direction1, average value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr50-d1-avg-csv.csv>`_
  - `CSV 1t1c PDR90, direction1, average value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-avg-csv.csv>`_
  - `CSV 1t1c PDR90, direction1, max value comparison <../../_static/vpp/latency-changes-2n-tx2-xl710-1t1c-pdr90-d1-max-csv.csv>`_

2n-aws-nitro50g
~~~~~~~~~~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR comparison <performance-changes-2n-aws-2t1c-ndr.html>`_
  - `HTML 4t2c NDR comparison <performance-changes-2n-aws-4t2c-ndr.html>`_
  - `ASCII 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-ndr.txt>`_
  - `ASCII 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-ndr.txt>`_
  - `CSV 2t1c NDR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-ndr-csv.csv>`_
  - `CSV 4t2c NDR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR comparison <performance-changes-2n-aws-2t1c-pdr.html>`_
  - `HTML 4t2c PDR comparison <performance-changes-2n-aws-4t2c-pdr.html>`_
  - `ASCII 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-pdr.txt>`_
  - `ASCII 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-pdr.txt>`_
  - `CSV 2t1c PDR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-pdr-csv.csv>`_
  - `CSV 4t2c PDR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR comparison <performance-changes-2n-aws-2t1c-mrr.html>`_
  - `HTML 4t2c MRR comparison <performance-changes-2n-aws-4t2c-mrr.html>`_
  - `ASCII 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-mrr.txt>`_
  - `ASCII 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-mrr.txt>`_
  - `CSV 2t1c MRR comparison <../../_static/vpp/performance-changes-2n-aws-2t1c-mrr-csv.csv>`_
  - `CSV 4t2c MRR comparison <../../_static/vpp/performance-changes-2n-aws-4t2c-mrr-csv.csv>`_
