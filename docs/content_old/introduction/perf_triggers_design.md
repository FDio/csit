---
bookHidden: true
title: "Performance Triggers Design"
---

# Performance Triggers Design

*Syntax*
  trigger_keyword [{tag1} {tag2}AND{tag3} !{tag4} !{tag5}]

*Inputs*
  - trigger_keyword for vpp-* jobs: 'perftest'
  - trigger_keyword for csit-* jobs: 'csit-perftest'
  - tags: existing CSIT tags [4]_ i.e. ip4base, ip6base, iacldst, memif

Set of default tags appended to user input, under control by CSIT
  - always-on for vpp-csit*.job: 'mrr' 'nic_intel_x710-da2' '1t1c'
  - if input with no tags, following set applied:
     - 'mrrANDnic_intel-x710AND1t1cAND64bANDip4base'
     - 'mrrANDnic_intel-x710AND1t1cAND78bANDip6base'
     - 'mrrANDnic_intel-x710AND1t1cAND64bANDl2bdbase'

Examples
  input: 'perftest'
    expanded: 'mrrANDnic_intel_x710-da2AND1t1cAND64bANDl2bdbase mrrANDnic_intel_x710-da2AND1t1cAND64bANDip4base mrrANDnic_intel_x710-da2AND1t1cAND78bANDip6base'
  input: 'perftest l2bdbase l2xcbase'
    expanded: 'mrrANDnic_intel_x710-da2ANDl2bdbase mrrANDnic_intel_x710-da2ANDl2xcbase'
  input: 'perftest ip4base !feature'
    expanded: 'mrrANDnic_intel_x710-da2ANDip4base' not 'feature'
  input: 'perftest ip4base !feature !lbond_dpdk'
    expanded: 'mrrANDnic_intel_x710-da2ANDip4base' not 'feature' not 'lbond_dpdk'
  input: 'perftestxyx ip4base !feature !lbond_dpdk'
    invalid: detected as error
  input: 'perftestip4base !feature !lbond_dpdk'
    invalid: detected as error
  input: 'perftest ip4base!feature!lbond_dpdk'
    invalid expand: 'mrrANDnic_intel_x710-da2ANDip4base!feature!lbond_dpdk'
    execution of RobotFramework will fail

Constrains
  Trigger keyword must be different for every job to avoid running multiple jobs
  at once. Trigger keyword must not be substring of job name or any other
  message printed by JJB bach to gerrit message which can lead to recursive
  execution.
