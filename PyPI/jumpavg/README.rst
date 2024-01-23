Jumpavg library
===============

Origins
-------

This library was developed as anomaly detection logic for "PAL" component
of CSIT_ (Continuous System and Integration Testing) project
of fd.io_ ("Fast Data"), one of LFN_ (Linux Foundation Networking) projects.
Currently still being primarily used in PAL's successor: CSIT-DASH_.

In order to make this code available in PyPI_ (Python Package Index),
the setuputils stuff (later converted to pyproject.toml) has been added,
but after some discussion, that directory_ ended up having
only a symlink to the original place of tightly coupled CSIT code.

Usage
-----

High level description
______________________

The main method is "classify", which partitions the input sequence of values
into consecutive "groups", so that standard deviation of samples within a group
is small.

The design decisions that went into the final algorithm are heavily influenced
by typical results seen in CSIT testing, so it is better to read about
the inner workings of the classification procedure in CSIT documentation,
especially the Minimum Description Length sub-chapter of `trend analysis`_.

Example
_______

A very basic example, showing some inputs and the structure of output.
The output is a single line, here shown wrapped for readability.

..  code-block:: python3

    >>> from jumpavg import classify
    >>> classify(values=[2.1, 3.1, 3.2], unit=0.1)
    BitCountingGroupList(max_value=3.2, unit=0.1, group_list=[BitCountingGroup(run_list=
    [2.1], max_value=3.2, unit=0.1, comment='normal', prev_avg=None, stats=AvgStdevStats
    (size=1, avg=2.1, stdev=0.0), cached_bits=6.044394119358453), BitCountingGroup(run_l
    ist=[3.1, 3.2], max_value=3.2, unit=0.1, comment='progression', prev_avg=2.1, stats=
    AvgStdevStats(size=2, avg=3.1500000000000004, stdev=0.050000000000000044), cached_bi
    ts=10.215241265313393)], bits_except_last=6.044394119358453)

Change log
----------

0.4.2: Should no longer divide by zero on empty inputs.

0.4.1: Fixed bug of not penalizing large stdev enough (at all for size 2 stats).

0.4.0: Added "unit" and "sbps" parameters so information content
is reasonable even if sample values are below one.

0.3.0: Considerable speedup by avoiding unneeded copy. Dataclasses used.
Mostly API compatible, but repr looks different.

0.2.0: API incompatible changes. Targeted to Python 3 now.

0.1.3: Changed stdev computation to avoid negative variance due to rounding errors.

0.1.2: First version published in PyPI.

.. _CSIT: https://wiki.fd.io/view/CSIT
.. _CSIT-DASH: https://csit.fd.io
.. _directory: https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg
.. _fd.io: https://fd.io/
.. _LFN: https://www.linuxfoundation.org/projects/networking/
.. _PyPI: https://pypi.org/
.. _trend analysis: https://csit.fd.io/cdocs/methodology/trending/analysis/#trend-analysis
