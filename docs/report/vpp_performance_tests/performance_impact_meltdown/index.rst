Performance Impact of Meltdown Patches
======================================

The following tables present performance impact on VPP after
applying patches addressing Meltdown (Variant3: Rogue Data Cache Load) security
 ulnerabilities. Incremental kernel patches are applied for Ubuntu 16.04LTS as
documented on `Ubuntu SpectreAndMeltdown page <https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/SpectreAndMeltdown>`_.
For detailed listing of used software versions and patches please refer
to :ref:`test_environment`.

NDR and PDR packet throughput results are compared for 1-core/1-thread,
2-cores/2-threads and 4-cores/4-threads VPP configurations, with
reference performance numbers coming from tests without the Meltdown
patches.

NDR throughput: Best 20 changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../_static/vpp/meltdown-impact-ndr-1t1c-top.csv

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
        ]{../_build/_static/vpp/meltdown-impact-ndr-1t1c-top.csv}
      }

NDR throughput: Worst 20 changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../_static/vpp/meltdown-impact-ndr-1t1c-bottom.csv

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
        ]{../_build/_static/vpp/meltdown-impact-ndr-1t1c-bottom.csv}
      }

.. only:: html

NDR throughput: All changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete results for all NDR tests are available in a CSV and pretty
ASCII formats:

  - `csv format for 1t1c <../../_static/vpp/meltdown-impact-ndr-1t1c-full.csv>`_,
  - `csv format for 2t2c <../../_static/vpp/meltdown-impact-ndr-2t2c-full.csv>`_,
  - `csv format for 4t4c <../../_static/vpp/meltdown-impact-ndr-4t4c-full.csv>`_,
  - `pretty ASCII format for 1t1c <../../_static/vpp/meltdown-impact-ndr-1t1c-full.txt>`_,
  - `pretty ASCII format for 2t2c <../../_static/vpp/meltdown-impact-ndr-2t2c-full.txt>`_,
  - `pretty ASCII format for 4t4c <../../_static/vpp/meltdown-impact-ndr-4t4c-full.txt>`_.

PDR throughput: Best 20 changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../_static/vpp/meltdown-impact-pdr-1t1c-top.csv

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
        ]{../_build/_static/vpp/meltdown-impact-pdr-1t1c-top.csv}
      }

PDR throughput: Worst 20 changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../_static/vpp/meltdown-impact-pdr-1t1c-bottom.csv

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
        ]{../_build/_static/vpp/meltdown-impact-pdr-1t1c-bottom.csv}
      }

.. only:: html

PDR throughput: All changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete results for all PDR tests are available in a CSV and pretty
ASCII formats:

  - `csv format for 1t1c <../../_static/vpp/meltdown-impact-pdr-1t1c-full.csv>`_,
  - `csv format for 2t2c <../../_static/vpp/meltdown-impact-pdr-2t2c-full.csv>`_,
  - `csv format for 4t4c <../../_static/vpp/meltdown-impact-pdr-4t4c-full.csv>`_,
  - `pretty ASCII format for 1t1c <../../_static/vpp/meltdown-impact-pdr-1t1c-full.txt>`_,
  - `pretty ASCII format for 2t2c <../../_static/vpp/meltdown-impact-pdr-2t2c-full.txt>`_,
  - `pretty ASCII format for 4t4c <../../_static/vpp/meltdown-impact-pdr-4t4c-full.txt>`_.
