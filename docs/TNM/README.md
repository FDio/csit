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
1. Add all data to the examples:
   - [mrr](examples/output_uti/uti_example_mrr.json)
   - [soak](examples/output_uti/uti_example_soak.json)

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
    + [mrr](examples/output_uti/uti_example_mrr.json)
    + [ndrpdr](examples/output_uti/uti_example_ndrpdr.json)
    + [soak](examples/output_uti/uti_example_soak.json)

-------------------------------------------------------------------------------
