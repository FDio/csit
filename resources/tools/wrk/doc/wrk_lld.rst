Onboarding of wrk as a http traffic generator in CSIT
-----------------------------------------------------

wrk is a modern HTTP benchmarking tool capable of generating significant
load when run on a single multi-core CPU.

An optional LuaJIT script can perform HTTP request generation, response
processing, and custom reporting.


wrk installation on TG node
'''''''''''''''''''''''''''

**Procedure:**

    #. Check if wrk is installed on the TG node.
    #. If not, install it.

**wrk instalation**

::

    # Install pre-requisites:
    sudo apt-get install build-essential libssl-dev git -y

    # Clone the wrk from git repo:
    git clone https://github.com/wg/wrk.git

    # Build the wrk:
    cd wrk
    make

    # Move the executable to somewhere in the PATH, e.q:
    sudo cp wrk /usr/local/bin


wrk traffic profile
'''''''''''''''''''

**The traffic profile can include these items:**

    - List of URLs - mandatory,
    - Number of CPUs used for wrk - mandatory,
    - Test duration - mandatory,
    - Number of threads - mandatory,
    - Number of connections - mandatory,
    - LuaJIT script - optional, defaults to no script,
    - HTTP header - optional, defaults to no header,
    - Latency - optional, defaults to False,
    - Timeout - optional, defaults to wrk default.

**List of URLs**

List of URLs for requests. Each URL is requested in a separate instance of wrk.
Type: list

*Example:*

::

    urls:
      - "http://192.168.1.1/1kB.bin"
      - "http://192.168.1.2/1kB.bin"
      - "http://192.168.1.3/1kB.bin"

**Number of CPUs used for wrk**

The number of CPUs used for wrk. The number of CPUs must be a multiplication
of the number of URLs.
Type: integer

*Example:*

::

    cpus: 6

.. note::

    The combinations of URLs and a number of CPUs create following use cases:

        - One URL and one CPU - One instance of wrk sends one request (URL) via one NIC
        - One URL and n CPUs - n instances of wrk send the same request (URL) via one or more NICs
        - n URLs and n CPUs - n instances of wrk send n requests (URL) via one or more NICs
        - n URLs and m CPUs, m = a * n - m instances of wrk send n requests (URL) via one or more NICs

**Test duration**

Duration of the test in seconds.
Type: integer

*Example:*

::

    duration: 30

**Number of threads**

Total number of threads to use by wrk to send traffic.
Type: integer

*Example:*

::

    nr-of-threads: 1

**Number of connections**

Total number of HTTP connections to keep open with each thread handling
N = connections / threads.
Type: integer

*Example:*

::

    nr-of-connections: 50

**LuaJIT script**

Path to LuaJIT script.
Type: string

*Example:*

::

    script: "scripts/report.lua"

**HTTP header**

HTTP header to add to request.
Type: string (taken as it is) or dictionary

*Example:*

::

    # Dictionary:
    header:
      Connection: "close"

or

::

    # String:
    header: "Connection: close"

**Latency**

Print detailed latency statistics.
Type: boolean

*Example:*

::

    latency: False

**Timeout**

Record a timeout if a response is not received within this amount of time.
Type: integer

::

    timeout: 5

**Example of a wrk traffic profile**

::

    urls:
      - "http://192.168.1.1/1kB.bin"
      - "http://192.168.1.2/1kB.bin"
      - "http://192.168.1.3/1kB.bin"
    cpus: 6
    duration: 30
    nr-of-threads: 1
    nr-of-connections: 50
    header:
      Connection: "close"
    latency: False
    timeout: 5


Running wrk
'''''''''''

TODO
