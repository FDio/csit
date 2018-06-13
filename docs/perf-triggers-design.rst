Introduction
------------

Previous gerrit triggers for performance tests (
*vpp-csit-verify-hw-perf-{branch}* and *csit-vpp-verify-hw-perf-{branch}*) are
listed in [1]_ with jjb definition in [2]_. Mapping of triggers to CSIT test RF
tags [4]_ driving the selection of test cases for execution is listed in [3]_.

Previous mappings of trigger to RF tags
---------------------------------------

(vpp-csit job) vpp-verify-perf-{**keyword**} OR (csit-vpp job) verify-perf-{**keyword**}
  - **acl**:
     - 'mrrANDnic_intel-x520-da2AND1t1cANDacl'
     - 'mrrANDnic_intel-x520-da2AND2t2cANDacl'
  - **ip4**:
     - 'mrrANDnic_intel-x520-da2AND1t1cANDip4base'
     - 'mrrANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m'
  - **ip6**
     - 'mrrANDnic_intel-x520-da2AND1t1cANDip6base'
     - 'mrrANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m'
  - **ipsechw**
     - 'pdrdiscANDnic_intel-xl710AND1t1cANDipsechw'
     - 'pdrdiscANDnic_intel-xl710AND2t2cANDipsechw'
     - 'mrrANDnic_intel-xl710AND1t1cANDipsechw'
     - 'mrrANDnic_intel-xl710AND2t2cANDipsechw'
  - **l2**
     - 'mrrANDnic_intel-x520-da2AND1t1cANDl2xcbase'
     - 'mrrANDnic_intel-x520-da2AND1t1cANDl2bdbase'
     - 'mrrANDnic_intel-x520-da2AND1t1cANDdot1q'
     - '!lbond_dpdk'
  - **lisp**
     - 'mrrANDnic_intel-x520-da2AND1t1cANDlisp'
  - **memif**
     - 'pdrdiscANDnic_intel-x520-da2AND1t1cANDmemif'
     - 'pdrdiscANDnic_intel-x520-da2AND2t2cANDmemif'
     - 'mrrANDnic_intel-x520-da2AND1t1cANDmemif'
     - 'mrrANDnic_intel-x520-da2AND2t2cANDmemif'
  - **vhost**
     - 'mrrANDnic_intel-x520-da2AND1t1cANDvhost'
     - '!lbond_dpdk'
  - **vxlan**
     - 'mrrANDnic_intel-x520-da2AND1t1cANDvxlan'
  - **srv6**
     - 'mrrANDsrv6AND1t1c'
     - 'mrrANDsrv6AND2t2c'

Proposal for mapping triggers to RF tags
----------------------------------------

*Goal*
  make it simpler to use, scalable, parametrize and prepare for full CI/CD
  automation.

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

Implementation
--------------

Implementation is separated into two projects.

CI-MANGEMENT
~~~~~~~~~~~~

https://gerrit.fd.io/r/#/c/13027/

Implementing new gerrit keyword `csit-perftest` in JJB for
*csit-vpp-perf-verify-{stream}* and `perftest` for
*vpp-csit-verify-hw-perf-{stream}* performance jobs.

::

  if [[ ${GERRIT_EVENT_TYPE} == 'comment-added' ]]; then
      TRIGGER=`echo ${GERRIT_EVENT_COMMENT_TEXT} \
          | grep -oE '(perftest$|perftest[[:space:]].+$)'`
  else
      TRIGGER=''
  fi
  # Export test type
  export TEST_TAG="VERIFY-PERF-PATCH"
  # Export test tags as string
  export TEST_TAG_STRING=${TRIGGER#$"perftest"}

Code is automatically detecting trigger type and parse the gerrit comment
massage. Stripped TAGs are exported as bash variable `$TEST_TAG_STRING` together
with `$TEST_TAG`.

CSIT
~~~~

https://gerrit.fd.io/r/#/c/13025/

Implementing `$TEST_TAG_STRING` variable post processing. String of TAGs is
automatically converted into array to be able to loop the items. If variable is
empty default set of TAGs is applied.

Array is then converted into Robot Framework parameter notation where every word
means new `--include` parameter. Having multiple words (multiple includes) means
logical OR in selection of test cases and could be applied to add additional
test cases that have no common more specific match. See exmaples section for
more details. Script also detects an exclamation mark before TAG that is
translated to as a `--exclude` parameter.

References
----------

.. [1] https://wiki.fd.io/view/CSIT/Jobs
.. [2] https://git.fd.io/ci-management/tree/jjb/vpp/vpp.yaml#n762
.. [3] https://git.fd.io/csit/tree/bootstrap-verify-perf.sh#n235
.. [4] https://git.fd.io/csit/tree/docs/tag_documentation.rst