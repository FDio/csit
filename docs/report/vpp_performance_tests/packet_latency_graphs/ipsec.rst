IPSec IPv4 Routing
==================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 50% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.


3n-hsw-x520
~~~~~~~~~~~

base-scale
----------

ndr
```

1t1c
....

2t2c
....

features
--------

ndr
```

1t1c
....

2t2c
....

3n-hsw-x710
~~~~~~~~~~~

base-scale
----------

ndr
```

1t1c
....

2t2c
....

features
--------

ndr
```

1t1c
....

2t2c
....

3n-hsw-xl710
~~~~~~~~~~~~

base-scale
----------

ndr
```

1t1c
....

2t2c
....

features
--------

ndr
```

1t1c
....

2t2c
....

3n-skx-x710
~~~~~~~~~~~

base-scale
----------

ndr
```

2t1c
....

4t2c
....

features
--------

ndr
```

2t1c
....

4t2c
....

3n-skx-xxv710
~~~~~~~~~~~~~

base-scale
----------

ndr
```

2t1c
....

4t2c
....

features
--------

ndr
```

2t1c
....

4t2c
....

2n-skx-x710
~~~~~~~~~~~

base-scale
----------

ndr
```

2t1c
....

4t2c
....

features
--------

ndr
```

2t1c
....

4t2c
....

2n-skx-xxv710
~~~~~~~~~~~~~

base-scale
----------

ndr
```

2t1c
....

4t2c
....

features
--------

ndr
```

2t1c
....

4t2c
....










