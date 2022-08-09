Jumpavg library
===============

Origins
-------

This library was developed as anomaly detection logic
for PAL_ (Presentation and Analysis Layer)
of CSIT_ (Continuous System and Integration Testing)
project of fd.io_ (Fast Data), one of LFN_
(Linux Foundation Networking) projects.

In order to make this code available in PyPI_ (Python Package Index),
the setuputils stuff has been added,
and the code has been moved into a separate directory_,
in order to not intervere of otherwise tightly coupled CSIT code.

Usage
-----

TODO.

Change log
----------

TODO: Move into separate file?

0.3.0: Considerable speedup by avoiding unneeded copy. Dataclasses used.
       Mostly API compatible, but repr looks different.

0.2.0: API incompatible changes. Targeted to Python 3 now.

0.1.3: Changed stdev computation to avoid negative variance due to rounding errors.

0.1.2: First version published in PyPI.

.. _PAL: https://wiki.fd.io/view/CSIT/Design_Optimizations#Presentation_and_Analytics_Layer
.. _CSIT: https://wiki.fd.io/view/CSIT
.. _fd.io: https://fd.io/
.. _LFN: https://www.linuxfoundation.org/projects/networking/
.. _PyPI: https://pypi.org/
.. _directory: https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg;hb=refs/heads/master
