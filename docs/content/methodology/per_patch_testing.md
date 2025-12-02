---
title: "Per-patch Testing"
weight: 5
---

# Per-patch Testing

A methodology similar to trending analysis is used for comparing performance
before a DUT code change is merged. This can act as a verify job to disallow
changes which would decrease performance without a good reason.

## Existing jobs

They are not started automatically, must be triggered on demand.
They allow full tag expressions, all types of perf tests are supported.

There are jobs available for multiple types of testbeds,
based on various processors.
Their Gerrit triggers words are of the form
"gha-run csit-{dut}-{node_arch} {testype}", where:

- dut: [vpp, dpdk, trex]
- testype: [perftest, bisecttest]
- node_arch: [3n-oct, 3n-emr, 2n-emr, 2n-grc, 2n-icx, 2n-spr, 2n-zn2, 3n-icx,
3n-alt, 3n-snr, 3na-spr, 3nb-spr]

## Test selection

Gerrit trigger line without any additional arguments selects
a small set of test cases to run.
If additional arguments are added to the Gerrit trigger, they are treated
as Robot tag expressions to select tests to run.
While very flexible, this method of test selection also allows the user
to accidentally select too high number of tests, blocking the testbed for days.

What follows is a list of explanations and recommendations
to help users to select the minimal set of tests cases.

### Multiple test cases in run

While Robot supports OR operator, it does not support parentheses,
so the OR operator is not very useful.
It is recommended to use space instead of OR operator.

Example template:
gha-run csit-vpp-2n-emr perftest {tag_expression_1} {tag_expression_2}

See below for more concrete examples.

### Suite tags

CSIT maintains broad Robot tags that can be used to select tests.

But it is not recommended to use them for test selection,
as it is not that easy to determine how many test cases are selected.

The recommended way is to look into CSIT repository first,
and locate a specific suite the user is interested in,
and use its suite tag. For example, "ethip4-ip4base" is a suite tag
selecting just one suite in CSIT git repository,
avoiding all scale, container, and other simialr variants.

### Fully specified tag expressions

Here is one template to select a single test case:
{test_type}AND{nic_model}AND{nic_driver}AND{cores}AND{frame_size}AND{suite_tag}
where the variables are all lower case (so AND operator stands out).

The fastest and the most widely used type of performance test is "mrr".
As an alternative, "ndrpdr" focuses on small losses (ax opposed to max load),
but takes longer to finish.
The nic_driver options depend on nic_model. For Intel cards "drv_avf"
(AVF plugin) and "drv_vfio_pci" (DPDK plugin) are popular, for Mellanox
"drv_mlx5_core". Currently, the performance using "drv_af_xdp" is not reliable
enough, so do not use it unless you are specifically testing for AF_XDP.

The most popular nic_model is "nic_intel-e810cq", but that is not available
on all testbed types.
It is safe to use "1c" for cores (unless you are suspecting multi-core
performance is affected differently) and "64b" for frame size ("78b" for ip6
and more for dot1q and other encapsulated traffic;
"1518b" is popular for ipsec and other CPU-bound tests).

As there are more test cases than CSIT can periodically test,
it is possible to encounter an old test case that currently fails.
To avoid that, you can look at "job specifications" files we use for periodic
testing, for example
[this one](https://github.com/FDio/csit/blob/master/resources/job_specifications/test_groups.yaml).

### Shortening triggers

Advanced users may use the following tricks to avoid writing long trigger
comments.

Robot supports glob matching, which can be used to select multiple suite tags at
once.

Not specifying one of 6 parts of the recommended expression pattern
will select all available options. For example not specifying nic_driver
for nic_intel-e810cq will select all 3 applicable drivers.
You can use NOT operator to reject some options (e.g. NOTdrv_af_xdp).
Beware, with NOT the order matters:
tag1ANDtag2NOTtag3 is not the same as tag1NOTtag3ANDtag2,
the latter is evaluated as tag1AND(NOT(tag3ANDtag2)).

Beware when not specifying nic_model. As a precaution,
CSIT code will insert the defailt NIC model for the tetsbed used.
Example: Specifying drv_rdma_core without specifying nic_model
will fail, as the default nic_model is nic_intel-e810cq
which does not support RDMA core driver.

### Complete example

A user wants to test a VPP change which may affect load balance whith bonding.
Searching tag documentation for "bonding" finds LBOND tag and its variants.
Searching CSIT git repository (directory tests/) finds 8 suite files,
all suited only for 3-node testbeds.
All suites are using vhost, but differ by the forwarding app inside VM
(DPDK or VPP), by the forwarding mode of VPP acting as host level vswitch
(MAC learning or cross connect), and by the number of DUT1-DUT2 links
available (1 or 2).

As not all NICs and testbeds offer enogh ports for 2 parallel DUT-DUT links,
the user looks at
[testbed specifications](https://github.com/FDio/csit/tree/master/topologies/available)
and finds that only e810xxv NIC on 3n-icx testbed matches the requirements.
Quick look into the suites confirm the smallest frame size is 64 bytes
(despite DOT1Q robot tag, as the encapsulation does not happen on TG-DUT links).
It is ok to use just 1 physical core, as 3n-icx has hyperthreading enabled,
so VPP vswitch will use 2 worker threads.

The user decides the vswitch forwarding mode is not important
(so choses cross connect as that has less CPU overhead),
but wants to test both NIC drivers (not AF_XDP), both apps in VM,
and both 1 and 2 parallel links.

After shortening, this is the trigger comment fianlly used:
gha-run csit-vpp-3n-icx perftest mrrANDnic_intel-e810cqAND1cAND64bAND?lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm\*NOTdrv_af_xdp

## Basic operation

The job builds VPP .deb packages for both the patch under test
(called "current") and its parent patch (called "parent").

For each test (from the set defined by tag expressions),
both builds are subjected to several trial measurements (in case of MRR).
Measured samples are grouped to "parent" sequence,
followed by "current" sequence. The same Minimal Description Length
algorithm as in trending is used to decide whether it is one big group,
or two smaller gropus. If it is one group, a "normal" result
is declared for the test. If it is two groups, and current average
is less then parent average, the test is declared a regression.
If it is two groups and current average is larger or equal,
the test is declared a progression.

The whole job fails (giving -1) if any test was declared a regression.
If a test fails, a fake result values are used,
so it is possible to use the job fo verify current fixes a test failing in parent
(if a test is not fixed, it is treated as a regression).

## Temporary specifics

The Minimal Description Length analysis is performed by
CSIT code equivalent to jumpavg-0.4.1 library available on PyPI.

In hopes of strengthening of signal (code performance) compared to noise
(all other factors influencing the measured values), several workarounds
are applied.

In contrast to trending, MRR trial duration is set to 10 seconds,
and only 5 samples are measured for each build.
Both parameters are set in ci-management.

This decreases sensitivity to regressions, but also decreases
probability of false positives.

## Console output

The following information as visible towards the end of Jenkins console output,
repeated for each analyzed test.

The original 5 values (or 1 for non-mrr) are visible in order they were measured.
The values after processing are also visible in output,
this time sorted by value (so people can see minimum and maximum).

The next output is difference of averages. It is the current average
minus the parent average, expressed as percentage of the parent average.

The next three outputs contain the jumpavg representation
of the two groups and a combined group.
Here, "bits" is the description length; for "current" sequence
it includes effect from "parent" average value
(jumpavg-0.4.1 penalizes sequences with too close averages).

Next, a sentence describing which grouping description is shorter,
and by how much bits.
Finally, the test result classification is visible.
