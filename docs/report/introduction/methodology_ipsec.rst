Internet Protocol Security (IPsec)
----------------------------------

VPP IPsec performance tests are executed for the following crypto
plugins:

- `crypto_native`, used for software based crypto leveraging CPU
  platform optimizations e.g. Intel's AES-NI instruction set.
- `dpdk_cryptodev`, used for hardware based crypto with Intel QAT PCIe
  cards.
- `crypto_sw_scheduler`, used to scheduler crypto work to dedicated async
  cores.

IPsec with VPP Native SW Crypto
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on VPP native crypto (`crypto_native` plugin):

+-------------------+------------------+----------------+------------------+
| VPP Crypto Engine | ESP Encryption   | ESP Integrity  | Scale Tested     |
+===================+==================+================+==================+
| crypto_native     | AES[128|256]-GCM | GCM            | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+
| crypto_native     | AES128-CBC       | SHA[256|512]   | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+

VPP IPsec with SW crypto are executed in both tunnel and policy modes,
with tests running on 3-node testbeds: 3n-skx.

IPsec with Intel QAT HW
^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on dpdk_cryptodev and Intel QAT 8950 (50G HW crypto card):

+-------------------+---------------------+------------------+----------------+------------------+
| VPP Crypto Engine | VPP Crypto Workers  | ESP Encryption   | ESP Integrity  | Scale Tested     |
+===================+=====================+==================+================+==================+
| dpdk_cryptodev    | async/QAT HW        | AES[128|256]-GCM | GCM            | 1, 4, 1k tunnels |
+-------------------+---------------------+------------------+----------------+------------------+
| dpdk_cryptodev    | async/QAT HW        | AES[128]-CBC     | SHA[256|512]   | 1, 4, 1k tunnels |
+-------------------+---------------------+------------------+----------------+------------------+

VPP IPsec with HW crypto are executed in both tunnel and policy modes,
with tests running on 3-node Haswell testbeds (3n-hsw), as these are the
only testbeds equipped with Intel QAT cards.

IPsec with VPP Crypto SW Scheduler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on VPP Crypto SW Scheduler (`crypto_sw_scheduler` plugin):

+---------------------+---------------------+------------------+----------------+--------------------+
| VPP Crypto Engine   | VPP Crypto Workers  | ESP Encryption   | ESP Integrity  | Scale Tested       |
+=====================+=====================+==================+================+====================+
| crypto_sw_scheduler | async/CPU cores     | AES[128|256]-GCM | GCM            | 1, 2, 4, 8 tunnels |
+---------------------+---------------------+------------------+----------------+--------------------+
| crypto_sw_scheduler | async/CPU cores     | AES[128]-CBC     | SHA[256|512]   | 1, 2, 4, 8 tunnels |
+---------------------+---------------------+------------------+----------------+--------------------+

VPP IPsec with Crypto SW Scheduler executed tunnel mode,
with tests running on 3-node testbeds: 3n-skx.

IPsec Uni-Directional Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^

*TODO Description to be added*

IPsec Deep SPD Policy Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^

*TODO Description to be added*
