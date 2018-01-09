Onboarding of wrk as a http traffic generator in CSIT
-----------------------------------------------------

wrk is a modern HTTP benchmarking tool capable of generating significant
load when run on a single multi-core CPU.

An optional LuaJIT script can perform HTTP request generation, response
processing, and custom reporting.


wrk installation on TG node
'''''''''''''''''''''''''''

**Procedure**

    #. Check if wrk is installed on the TG node.
    #. If not, install it.

**wrk installation**

::

    # Install pre-requisites:
    sudo apt-get install build-essential libssl-dev git -y

    # Get the specified version:
    wget ${WRK_DWNLD_PATH}/${WRK_TAR}
    tar xzf ${WRK_TAR}
    cd wrk-${WRK_VERSION}

    # Build the wrk:
    cd wrk
    make

    # Move the executable to somewhere in the PATH, e.q:
    sudo cp wrk /usr/local/bin


wrk traffic profile
'''''''''''''''''''

**The traffic profile can include these items:**

    - List of URLs - mandatory,
    - The first CPU used to run wrk - mandatory,
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

**The first CPU used to run wrk**
The first CPU used to run wrk. The other CPUs follow this one.
Type: integer

*Example:*

::

    first-cpu: 1

**Number of CPUs used for wrk**

The number of CPUs used for wrk. The number of CPUs must be a multiplication
of the number of URLs.
Type: integer

*Example:*

::

    cpus: 6

.. note::

    The combinations of URLs and a number of CPUs create following use cases:

        - One URL and one CPU - One instance of wrk sends one request (URL) via
          one NIC
        - One URL and n CPUs - n instances of wrk send the same request (URL)
          via one or more NICs
        - n URLs and n CPUs - n instances of wrk send n requests (URL) via one
          or more NICs
        - n URLs and m CPUs, m = a * n - m instances of wrk send n requests
          (URL) via one or more NICs

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

For more information see: https://github.com/wg/wrk/blob/master/SCRIPTING

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

**Examples of a wrk traffic profile**

*Get the number of connections per second:*

- Use 3 CPUs to send 3 different requests via 3 NICs.
- The test takes 30 seconds.
- wrk sends traffic in one thread per CPU.
- There will be open max 50 connection at the same time.
- The header is set to 'Connection: "close"' so wrk opens separate connection
  for each request. Then the number of requests equals to the number of
  connections.
- Timeout for responses from the server is set to 5 seconds.

::

    urls:
      - "http://192.168.1.1/0B.bin"
      - "http://192.168.1.2/0B.bin"
      - "http://192.168.1.3/0B.bin"
    cpus: 3
    duration: 30
    nr-of-threads: 1
    nr-of-connections: 50
    header:
      Connection: "close"
    timeout: 5

*Get the number of requests per second:*

- Use 3 CPUs to send 3 different requests via 3 NICs.
- The test takes 30 seconds.
- wrk sends traffic in one thread per CPU.
- There will be max 50 concurrent open connections.

::

    urls:
      - "http://192.168.1.1/1kB.bin"
      - "http://192.168.1.2/1kB.bin"
      - "http://192.168.1.3/1kB.bin"
    cpus: 3
    duration: 30
    nr-of-threads: 1
    nr-of-connections: 50

*Get the bandwidth:*

- Use 3 CPUs to send 3 different requests via 3 NICs.
- The test takes 30 seconds.
- wrk sends traffic in one thread per CPU.
- There will be open max 50 connection at the same time.
- Timeout for responses from the server is set to 5 seconds.

::

    urls:
      - "http://192.168.1.1/1MB.bin"
      - "http://192.168.1.2/1MB.bin"
      - "http://192.168.1.3/1MB.bin"
    cpus: 3
    duration: 30
    nr-of-threads: 1
    nr-of-connections: 50
    timeout: 5


Running wrk
'''''''''''

**Suite setup phase**

CSIT framework checks if wrk is installed on the TG node. If not, or if the
installation is forced, it installs it on the TG node.

*Procedure:*

    #. Make sure TRex is stopped.
    #. Bind used TG interfaces to corresponding drivers (defined in the topology
       file).
    #. If the wrk installation is forced:

        - Destroy existing wrk

    #. If the wrk installation is not forced:

        - Check if wrk is installed.
        - If installed, exit.

    #. Clone wrk from git (https://github.com/wg/wrk.git)
    #. Build wrk.
    #. Copy the executable to /usr/local/bin so it is in the PATH.

**Test phase**

*Procedure:*

#. Read the wrk traffic profile.
#. Verify the profile.
#. Use the information from the profile to set the wrk parameters.
#. Run wrk.
#. Read the output.
#. Evaluate and log the output.

