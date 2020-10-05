Internet Protocol Security (IPsec)
----------------------------------

VPP IPsec performance tests are executed for the following crypto
plugins:

- `crypto_native`, used for software based crypto leveraging CPU
  platform optimizations e.g. Intel's AES-NI instruction set.
- `crypto_ipsecmb`, used for hardware based crypto with Intel QAT PCIe
  cards.

IPsec with VPP Native SW Crypto
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on VPP native crypto (`crypto_native` plugin):

+-------------------+------------------+----------------+------------------+
| VPP Crypto Engine | ESP Encryption   | ESP Integrity  | Scale Tested     |
+===================+===================+===============+==================+
| crypto_native     | AES[128|256]-GCM | GCM            | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+
| crypto_native     | AES128-CBC       | SHA[256|512]   | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+

VPP IPsec with SW crypto are executed in both tunnel and policy modes,
with tests running on 3-node testbeds: 3n-hsw and 3n-skx.

IPsec with Intel QAT HW
^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on ipsecmb library (`crypto_ipsecmb` plugin) and Intel QAT 8950 (50G HW
crypto card):

dpdk_cryptodev

+-------------------+---------------------+------------------+----------------+------------------+
| VPP Crypto Engine | VPP Crypto Workers  | ESP Encryption   | ESP Integrity  | Scale Tested     |
+===================+=====================+==================+================+==================+
| crypto_ipsecmb    | sync/all workers    | AES[128|256]-GCM | GCM            | 1, 1k tunnels    |
+-------------------+---------------------+------------------+----------------+------------------+
| crypto_ipsecmb    | sync/all workers    | AES[128]-CBC     | SHA[256|512]   | 1, 1k tunnels    |
+-------------------+---------------------+------------------+----------------+------------------+
| crypto_ipsecmb    | async/crypto worker | AES[128|256]-GCM | GCM            | 1, 4, 1k tunnels |
+-------------------+---------------------+------------------+----------------+------------------+
| crypto_ipsecmb    | async/crypto worker | AES[128]-CBC     | SHA[256|512]   | 1, 4, 1k tunnels |
+-------------------+---------------------+------------------+----------------+------------------+

VPP IPsec with HW crypto are executed in both tunnel and policy modes,
with tests running on 3-node Haswell testbeds (3n-hsw), as these are the
only testbeds equipped with Intel QAT cards.
