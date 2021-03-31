Multiple Loss Ratio Search library
==================================

Origins
-------

This library was developed as a speedup for traditional binary search
in CSIT_ (Continuous System and Integration Testing) project of fd.io_
(Fast Data), one of LFN_ (Linux Foundation Networking) projects.

In order to make this code available in PyPI_ (Python Package Index),
the setuputils stuff has been added,
but after some discussion, the export directory_
is only a symlink to the original place of tightly coupled CSIT code.

Change log
----------

0.4.0: Considarable logic improvements, more than two target ratios supported.
API is not backward compatible with previous versions.

0.3.0: Migrated to Python 3.6, small code quality improvements.

0.2.0: Optional parameter "doublings" has been added.

0.1.1: First officially released version.

Usage
-----

TODO.

Operation logic
---------------

The latest published `IETF draft`_ describes logic of version 0.3,
version 0.4 logic will be descibed in next draft version.

.. _CSIT: https://wiki.fd.io/view/CSIT
.. _fd.io: https://fd.io/
.. _LFN: https://www.linuxfoundation.org/projects/networking/
.. _PyPI: https://pypi.org/project/MLRsearch/
.. _directory: https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch;hb=refs/heads/master
.. _IETF draft: https://tools.ietf.org/html/draft-ietf-bmwg-mlrsearch-00
