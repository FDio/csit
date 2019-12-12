Using RF tags in Gerrit comment triggers
----------------------------------------

*Syntax*
  trigger_word [{tag1} {tag2}AND{tag3}NOT{tag4} !{tag5}]

*Inputs*
  - trigger_word for vpp-* perf jobs: 'perftest-{node_arch}'
    - Example: 'perftest-2n-skx'
  - trigger_word for csit-* vpp perf jobs: 'csit-{node_arch}-perftest'
    - Example: 'csit-2n-clx-perftest'
  - trigger_word for csit-* dpdk perf jobs: 'csit-dpdk-{node_arch}-perftest'
    - Example: 'csit-3n-hsw-perftest'
  - tags: existing CSIT tags [1]_ in lowercase.
    - Examples: ip4base, ip6base, iacldst, memif

*Logic*
  - Tag expressions starting with ! generate --exclude arguments to robot.
  - Tag expressions not starting with ! generate --include arguments to robot.
  - Space delimits diferent sets. A test case is selected if it matches:
    - At least one include set,
    - and at the same time no exclude set.
  - A testcase matches a set if:
    - It contains the starting tag and each tag after AND.
    - And at the same time it contains no tag after NOT.
  - It is possible to use NOT in expressions starting with !.
  - Brackets are not available, some trigger lines can get very long.

If no expression follows the trigger word, some tag expressions are applied
to prevent starting too many testcases.
If the reserved testbed lacks some resource (NIC type, double link),
additional --exclude arguments are added automatically.
See the bash function select_tags for the current details on both points.

References
----------

.. [1] https://git.fd.io/csit/tree/docs/tag_documentation.rst
