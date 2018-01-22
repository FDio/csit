Performance Impact of Spectre Patches
======================================

The following tables present the impact of Spectre patches on the VPP
performance. NDR and PDR throughput was measured compared for 1-core/1-thread,
2-cores/2-threads and 4-cores/4-threads VPP configurations.

NDR throughput: Top 20 improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_impact_meltdown/spectre-impact-ndr-1t1c-top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/spectre-impact-ndr-1t1c-top.csv}
      }

NDR throughput: Bottom 20 results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_impact_meltdown/spectre-impact-ndr-1t1c-bottom.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/spectre-impact-ndr-1t1c-bottom.csv}
      }

.. only:: html

   The full results for NDR are available in

      - `csv format for 1t1c <spectre-impact-ndr-1t1c-full.csv>`_,
      - `csv format for 2t2c <spectre-impact-ndr-2t2c-full.csv>`_,
      - `csv format for 4t4c <spectre-impact-ndr-4t4c-full.csv>`_,
      - `pretty ASCII format for 1t1c <spectre-impact-ndr-1t1c-full.txt>`_,
      - `pretty ASCII format for 2t2c <spectre-impact-ndr-2t2c-full.txt>`_,
      - `pretty ASCII format for 4t4c <spectre-impact-ndr-4t4c-full.txt>`_.

PDR throughput: Top 20 results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_impact_meltdown/spectre-impact-pdr-1t1c-top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/spectre-impact-pdr-1t1c-top.csv}
      }

PDR throughput: Bottom 20 results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_impact_meltdown/spectre-impact-pdr-1t1c-bottom.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/spectre-impact-pdr-1t1c-bottom.csv}
      }

.. only:: html

   The full results for NDR are available in

      - `csv format for 1t1c <spectre-impact-pdr-1t1c-full.csv>`_,
      - `csv format for 2t2c <spectre-impact-pdr-2t2c-full.csv>`_,
      - `csv format for 4t4c <spectre-impact-pdr-4t4c-full.csv>`_,
      - `pretty ASCII format for 1t1c <spectre-impact-pdr-1t1c-full.txt>`_,
      - `pretty ASCII format for 2t2c <spectre-impact-pdr-2t2c-full.txt>`_,
      - `pretty ASCII format for 4t4c <spectre-impact-pdr-4t4c-full.txt>`_.
