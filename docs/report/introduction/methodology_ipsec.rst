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
+===================+==================+================+==================+
| crypto_native     | AES[128|256]-GCM | GCM            | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+
| crypto_native     | AES128-CBC       | SHA[256|512]   | 1 to 60k tunnels |
+-------------------+------------------+----------------+------------------+

VPP IPsec with SW crypto are executed in both tunnel and policy modes,
with tests running on 3-node testbeds: 3n-skx, 3n-tsh.

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

IPsec with Async Crypto Feature Workers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*TODO Description to be added*

IPsec Uni-Directional Tests with VPP Native SW Crypto
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec uni-directional test cases
relying on VPP native crypto (`crypto_native` plugin) in tunnel mode:

+-------------------+------------------+---------------+--------------------+
| VPP Crypto Engine | ESP Encryption   | ESP Integrity | Scale Tested       |
+===================+==================+===============+====================+
| crypto_native     | AES[128|256]-GCM | GCM           | 4, 1k, 10k tunnels |
+-------------------+------------------+---------------+--------------------+
| crypto_native     | AES128-CBC       | SHA[512]      | 4, 1k, 10k tunnels |
+-------------------+------------------+---------------+--------------------+

In policy mode:

+-------------------+----------------+---------------+-------------------+
| VPP Crypto Engine | ESP Encryption | ESP Integrity | Scale Tested      |
+===================+================+===============+===================+
| crypto_native     | AES[256]-GCM   | GCM           | 1, 40, 1k tunnels |
+-------------------+----------------+---------------+-------------------+

The tests are running on 2-node testbeds: 2n-tx2. The uni-directional tests
are partially addressing a weakness in 2-node testbed setups with T-Rex as
the traffic generator. With just one DUT node, we can either encrypt or decrypt
traffic in each direction.

The testcases are only doing encryption - packets are encrypted on the DUT and
then arrive at TG where no additional packet processing is needed (just
counting packets).

Decryption would require that the traffic generator generated encrypted packets
which the DUT then would decrypt. However, T-Rex does not have the capability
to encrypt packets.
