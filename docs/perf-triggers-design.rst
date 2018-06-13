Introduction
------------

Previous gerrit triggers for vpp performance tests (vpp-csit-verify-hw-
perf-{branch} and csit-vpp-verify-hw-perf-{branch}) are listed in [1] with jjb
definition in [2]. Mapping of triggers to CSIT test RF tags [4] driving the
selection of test cases for execution is listed in [3].

Previous mappings of trigger to RF tags
---------------------------------------

(vpp-csit*) vpp-verify-perf-{keyword}
(csit-vpp*) verify-perf-{keyword}

  {acl} 'mrrANDnic_intel-x520-da2AND1t1cANDacl' 'mrrANDnic_intel-x520-da2AND2t2cANDacl'
  {ip4} 'mrrANDnic_intel-x520-da2AND1t1cANDip4base' 'mrrANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m'
  {ip6} 'mrrANDnic_intel-x520-da2AND1t1cANDip6base' 'mrrANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m'
  {ipsechw} 'pdrdiscANDnic_intel-xl710AND1t1cANDipsechw' 'pdrdiscANDnic_intel-xl710AND2t2cANDipsechw' 'mrrANDnic_intel-xl710AND1t1cANDipsechw' 'mrrANDnic_intel-xl710AND2t2cANDipsechw'
  {l2} 'mrrANDnic_intel-x520-da2AND1t1cANDl2xcbase' 'mrrANDnic_intel-x520-da2AND1t1cANDl2bdbase' 'mrrANDnic_intel-x520-da2AND1t1cANDdot1q' '!lbond_dpdk'
  {lisp} 'mrrANDnic_intel-x520-da2AND1t1cANDlisp'
  {memif} 'pdrdiscANDnic_intel-x520-da2AND1t1cANDmemif' 'pdrdiscANDnic_intel-x520-da2AND2t2cANDmemif' 'mrrANDnic_intel-x520-da2AND1t1cANDmemif' 'mrrANDnic_intel-x520-da2AND2t2cANDmemif'
  {vhost} 'mrrANDnic_intel-x520-da2AND1t1cANDvhost' '!lbond_dpdk'
  {vxlan} 'mrrANDnic_intel-x520-da2AND1t1cANDvxlan'
  {srv6} 'mrrANDsrv6AND1t1c' 'mrrANDsrv6AND2t2c'

Proposal for mapping triggers to RF tags
----------------------------------------

Goal: make it simpler to use, parametrize and prepare for full CI/CD automation.

Syntax: trigger_keyword [{tag1} {tag2}AND{tag3} !{tag4} !{tag5}]

Inputs:
  trigger_keyword vpp-* jobs: 'perftest'
  trigger_keyword csit-* jobs: 'csit-perftest'
  tags: existing CSIT tags i.e. ip4base, ip6base, iacldst, memif...

Set of default tags appended to user input, under control by CSIT:
  always-on: mrr 1t1c nic_model
  if input with no tags: l2bdbase ip4base ip6base

Examples:
  input: 'perftest'
    expanded: 'mrrANDnic_intel_x710-da2AND1t1cAND64bANDl2bdbase mrrANDnic_intel_x710-da2AND1t1cAND64bANDip4base mrrANDnic_intel_x710-da2AND1t1cAND64bAND/ip6base'
  input: 'perftest l2bdbase l2xcbase'
    expanded: 'mrrANDnic_intel_x710-da2ANDl2bdbase mrrANDnic_intel_x710-da2ANDl2xcbase'
  input: 'perftest ip4base !feature'
    expanded: 'mrrANDnic_intel_x710-da2ANDip4base' not 'feature'
  input: 'perftest ip4base !feature !lbond_dpdk'
    expanded: 'mrrANDnic_intel_x710-da2ANDip4base' not 'feature' not 'lbond_dpdk'

Notes:
  trigger_keyword parsing is implemented via grep regular expression syntax:
  `grep -oE '(perftest)+[[:space:]](.+)'`. Logical AND between TAGs means that
  both TAGs are applied on test case. Space between TAGs means 'OR'. This can be
  used to select multiple testcases like ip4base and l2xc in single run. Exclude
  is possible by adding !(exclamation mark) before TAG.

References
----------

[1] https://wiki.fd.io/view/CSIT/Jobs
[2] https://git.fd.io/ci-management/tree/jjb/vpp/vpp.yaml#n762
[3] https://git.fd.io/csit/tree/bootstrap-verify-perf.sh#n235
[4] https://git.fd.io/csit/tree/docs/tag_documentation.rst