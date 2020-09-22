-------------------------------------------------------------------------------
# CSIT-2.0

Version 0.1.0

## Changelog

| Version  | Changes                                                          |
|----------|------------------------------------------------------------------|
| 0.1.0    | Initial revision                                                 |

## TODOs

1. Add [Unified Test Interface Lifecycle](design.md#unified-test-interface-lifecycle).
1. Add [Implementation](design.md#implementation) details.

## Content

- [Design](design.md)
- [Suite Specification](suite_specification.json)
- [Unified Test Interface](unified_test_interface.json)
- [Examples](examples)
  * [Input Test Definition](examples/input_test_definition)
    + [Suites](examples/input_test_definition/suites)
      - [ethip4-ip4base](examples/input_test_definition/suites/2n1l-10ge2p1x710-ethip4-ip4base-ndrpdr.json)
    + [Topology](examples/input_test_definition/topology)
      - [2n-clx](examples/input_test_definition/topology/lf_2n_clx_testbed27.yaml)
  * [UTI](examples/output_uti)
    + [mrr](examples/output_uti/64b-1c-eth-l2patch-mrr.json)
    + [ndrpdr](examples/output_uti/78b-1c-ethip6-ip6base-ndrpdr.json)
    + [ndrpdr cps](examples/output_uti/64b-2c-avf-ethip4udp-nat44ed-h4096-p63-s258048-cps-ndrpdr.json)
    + [soak](examples/output_uti/64b-1c-ethip4-ip4base-soak.json)
    + [reconf](examples/output_uti/64b-1c-ethip4ipsec60000tnlsw-1atnl-ip4base-int-aes128cbc-hmac256sha-reconf.json)
    + [hoststack 1](examples/output_uti/1280b-1c-eth-ip4udpquicscale1cl10s-vppecho-bps.json)
    + [hoststack 2](examples/output_uti/1460b-1c-eth-ip4tcpbase-nsim-ldpreload-iperf3-bps.json)
    + [device](examples/output_uti/64b-ethipv4-ip4base-dev.json)

-------------------------------------------------------------------------------
