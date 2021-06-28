VSAP ab with nginx
^^^^^^^^^^^^^^^^^^

`VSAP (VPP Stack Acceleration Project) <https://wiki.fd.io/view/VSAP>`_
aims to establish an industry user space application ecosystem based on
the VPP hoststack.  As a pre-requisite to adapting open source applications
using VPP Communications Library to accelerate performance, the VSAP team
has introduced baseline tests utilizing the LD_PRELOAD mechanism to capture
baseline performance data.

`AB (Apache HTTP server benchmarking tool) <https://httpd.apache.org/docs/2.4/programs/ab.html>`_
is used for measuring the maximum connections-per-second and requests-per-second.

`NGINX <https://www.nginx.com/>`_ is a popular open source HTTP server
application.  Because NGINX utilizes the POSIX socket interface APIs, the test
configuration uses the LD_PRELOAD mechanism to connect NGINX to the VPP
Hoststack using the VPP Communications Library (VCL) LD_PRELOAD library
(libvcl_ldpreload.so).

In the future, a version of NGINX which has been modified to
directly use the VCL application APIs will be added to determine the
difference in performance of 'VCL Native' applications versus utilizing
LD_PRELOAD which inherently has more overhead and other limitations.

The test configuration is as follows:

::

           TG     Network         DUT
         [ AB ]=============[ VPP -> nginx ]

where,

1. nginx attaches to VPP and listens on TCP port 80
2. ab runs CPS and RPS tests with packets flowing from the Test Generator node,
   across 100G NICs, through VPP hoststack to NGINX.
3. At the end of the tests, the results are reported by AB.
