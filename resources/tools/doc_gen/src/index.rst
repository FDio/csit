.. |csit| replace:: Continuous System Integration and Testing


|csit| Description
==================

#. Development of software code for fully automated VPP code testing, functionality, performance, regression and new functions.
#. Execution of CSIT test suites on VPP code running on LF FD.io virtual and physical compute environments.
#. Integration with FD.io continuous integration systems (Gerrit, Jenkins and such).
#. Identified existing FD.io project dependencies and interactions:
    - vpp - Vector Packet Processing.
    - honeycomb - Honeycomb Agent for management plane testing.
    - ci-management - Management repo for Jenkins Job Builder, script and management related to the Jenkins CI configuration.

Project Scope
-------------

#. Automated regression testing of VPP code changes
    - Functionality of VPP data plane, network control plane, management plane against functional specifications.
    - Performance of VPP data plane including non-drop-rate packet throughput and delay, against established reference benchmarks.
    - Performance of network control plane against established reference benchmarks.
    - Performance of management plane against established reference benchmarks.
#. Test case definitions driven by supported and planned VPP functionality, interfaces and performance:
    - Uni-dimensional tests: Data plane, (Network) Control plane, Management plane.
    - Multi-dimensional tests: Use case driven.
#. Integration with FD.io Continuous Integration system including FD.io Gerrit and Jenkins
    - Automated test execution triggered by VPP-VERIFY jobs other VPP and CSIT project jobs.
#. Integration with LF VPP test execution environment
    - Functional tests execution on LF hosted VM environment.
    - Performance and functional tests execution on LF hosted physical compute environment.
    - Subset of tests executed on LF hosted physical compute running VIRL (Virtual Internet Routing Lab).

|csit| Documentation
--------------------

Python Library
##############

.. toctree::
   :maxdepth: 2
   :glob:
   
   resources.libraries.python

Robot Library
#############

.. toctree::
   :maxdepth: 2
   :glob:
   
   resources.libraries.robot

Functional Tests
################

.. toctree::
   :maxdepth: 3
   :glob:
   
   tests.func

Performance Tests
#################

.. toctree::
   :maxdepth: 2
   :glob:
   
   tests.perf
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
