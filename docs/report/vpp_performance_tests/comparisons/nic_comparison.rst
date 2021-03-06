
.. _vpp_compare_nics_release:

NICs Comparison
---------------

Relative comparison of VPP packet throughput (NDR, PDR and MRR) between
NICs (measured for |csit-release) is calculated from results of tests
running on 3n-skx, 2n-skx testbeds.

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

    - `build logs from FD.io vpp performance job 3n-skx`_,
    - `build logs from FD.io vpp performance job 2n-skx`_

    with RF result files csit-vpp-perf-|srelease|-\*.zip
    `archived here <../../_static/archive/>`_.

3n-skx
~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-2t1c-nics-ndr.html>`_
  - `HTML 4t2c NDR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-4t2c-nics-ndr.html>`_
  - `ASCII 2t1c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-ndr.txt>`_
  - `ASCII 4t2c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-ndr.txt>`_
  - `CSV 2t1c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-ndr-csv.csv>`_
  - `CSV 4t2c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-2t1c-nics-pdr.html>`_
  - `HTML 4t2c PDR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-4t2c-nics-pdr.html>`_
  - `ASCII 2t1c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-pdr.txt>`_
  - `ASCII 4t2c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-pdr.txt>`_
  - `CSV 2t1c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-pdr-csv.csv>`_
  - `CSV 4t2c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-2t1c-nics-mrr.html>`_
  - `HTML 4t2c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-4t2c-nics-mrr.html>`_
  - `HTML 8t4c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-3n-skx-8t4c-nics-mrr.html>`_
  - `ASCII 2t1c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-mrr.txt>`_
  - `ASCII 4t2c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-mrr.txt>`_
  - `ASCII 8t4c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-8t4c-nics-mrr.txt>`_
  - `CSV 2t1c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-2t1c-nics-mrr-csv.csv>`_
  - `CSV 4t2c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-4t2c-nics-mrr-csv.csv>`_
  - `CSV 8t4c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-3n-skx-8t4c-nics-mrr-csv.csv>`_

2n-skx
~~~~~~

NDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c NDR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-2t1c-nics-ndr.html>`_
  - `HTML 4t2c NDR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-4t2c-nics-ndr.html>`_
  - `ASCII 2t1c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-ndr.txt>`_
  - `ASCII 4t2c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-ndr.txt>`_
  - `CSV 2t1c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-ndr-csv.csv>`_
  - `CSV 4t2c NDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-ndr-csv.csv>`_

PDR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c PDR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-2t1c-nics-pdr.html>`_
  - `HTML 4t2c PDR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-4t2c-nics-pdr.html>`_
  - `ASCII 2t1c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-pdr.txt>`_
  - `ASCII 4t2c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-pdr.txt>`_
  - `CSV 2t1c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-pdr-csv.csv>`_
  - `CSV 4t2c PDR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-pdr-csv.csv>`_

MRR Comparison
``````````````

Comparison tables in HTML, ASCII and CSV formats:

  - `HTML 2t1c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-2t1c-nics-mrr.html>`_
  - `HTML 4t2c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-4t2c-nics-mrr.html>`_
  - `HTML 8t4c MRR Intel-x710 and Intel-xxv710 comparison <performance-changes-2n-skx-8t4c-nics-mrr.html>`_
  - `ASCII 2t1c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-mrr.txt>`_
  - `ASCII 4t2c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-mrr.txt>`_
  - `ASCII 8t4c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-8t4c-nics-mrr.txt>`_
  - `CSV 2t1c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-2t1c-nics-mrr-csv.csv>`_
  - `CSV 4t2c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-4t2c-nics-mrr-csv.csv>`_
  - `CSV 8t4c MRR Intel-x710 and Intel-xxv710 comparison <../../_static/vpp/performance-changes-2n-skx-8t4c-nics-mrr-csv.csv>`_
