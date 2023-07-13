# Jumpavg library

## Origins

This library was developed as anomaly detection logic
for [PAL](https://wiki.fd.io/view/CSIT/Design_Optimizations#Presentation_and_Analytics_Layer "Presentation and Analysis Layer")
of [CSIT](https://wiki.fd.io/view/CSIT "Continuous System and Integration Testing")
project of [fd.io](https://fd.io/ "Fast Data"),
one of [LFN](https://www.linuxfoundation.org/projects/networking/ "Linux Foundation Networking") projects.

Currently still being primarily used in PAL's successor [CSIT-DASH](https://csit.fd.io).

In order to make this code available in [PyPI](https://pypi.org/ "Python Package Index"),
the setuputils stuff has been added,
and the code has been moved into a separate [directory](https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg),
in order to not intervere of otherwise tightly coupled CSIT code.

## Usage

TODO.

## Change log

TODO: Move into a separate file?

+ 0.4.1: Fixed bug of not penalizing large stdev enough (at all for size 2 stats).

+ 0.4.0: Added "unit" and "sbps" parameters so information content
  is reasonable even if sample values are below one.

+ 0.3.0: Considerable speedup by avoiding unneeded copy. Dataclasses used.
  Mostly API compatible, but repr looks different.

+ 0.2.0: API incompatible changes. Targeted to Python 3 now.

+ 0.1.3: Changed stdev computation to avoid negative variance due to rounding errors.

+ 0.1.2: First version published in PyPI.
