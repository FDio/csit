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

- ESP-AES[128|256]-GCM, tested in IPsec tunnel interface and policy
  modes, scale tested 1 to 60k tunnels.
- ESP-AES128-CBC and ESP-SHA256, tested in IPsec tunnel interface and
  policy modes, scale tested 1 to 60k tunnels.

All tests are executed on 3-node testbeds: 3n-hsw and 3n-skx.

IPsec with Intel QAT HW
^^^^^^^^^^^^^^^^^^^^^^^

Currently |csit-release| implements following IPsec test cases relying
on ipsecmb library (`crypto_ipsecmb` plugin) and Intel QAT 8950 (50G HW
crypto card):

- ESP-AES[128|256]-GCM, tested in IPsec tunnel interface, scale tested 1
  and 1k tunnels.

- ESP-AES[128|256]-GCM Async for jumbo flows, tested in IPsec tunnel
  interface and policy modes, scale tested 1 and 1k tunnels.

All tests are executed on 3-node Haswell testbeds (3n-hsw), as these are
the only testbeds equipped with Intel QAT cards.
