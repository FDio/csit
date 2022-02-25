<!-- MarkdownTOC autolink="true" -->

- [TODO sequence](#todo-sequence)
- [sut infra hw](#sut-infra-hw)
- [tg infra](#tg-infra)
- [sut and tg infra config](#sut-and-tg-infra-config)
- [tg infra config](#tg-infra-config)
- [telemetry](#telemetry)
- [ubuntu 22.04](#ubuntu-2204)

<!-- /MarkdownTOC -->

# TODO sequence

- sut and tg infra, new yul1 hw builds
  + seq-2
    * re-fit of MLX NICs into 3x 2n-clx TG 2p100ge, to be used for CVL testing on SUTs
      - For existing Intel Xeon Cascadelake testbeds
        + MCX556A-EDAT NIC 2p100GbE - $1,195.00
        + need 4 NICs (3x TG, 1 TG loopback, 1 spare) => 5 NICs
        + procurement authorized by TSC on Thu 24-feb
    * TODO2 install 5x MCX556A-EDAT NIC 2p100GbE
  + seq-3
    * 10x supermicro icx ETA TBC
    * TODO1 order Nx MCX556A-EDAT NIC 2p100GbE
      - re-confirm all pluggables+cables are available on site in YUL1
    * TODO2 install Nx MCX556A-EDAT NIC 2p100GbE
  + seq-4
    * fit of 3x MLX NICs (1 in TG, 2 in SUTs) into 1x 3n-alt testbeds, to be used for MLX testing on SUTs
    * TODO1 order 3x MCX556A-EDAT NIC 2p100GbE
      - re-confirm all pluggables+cables are available on site in YUL1
    * TODO2 install 3x MCX556A-EDAT NIC 2p100GbE
  + seq-5
    * fit of MLX NICs into 3x icx testbeds (TG), to be used for MLX and CVL testing on SUTs
  + seq-6
    * re-purpose and/or decommission all skx perf testbeds

- aws builds
  + seq-1
    * calibration of c5n 2n and 3n instances
      - trex mlrsearch impact on c5n 4xl packet drops due to admin rate limit
        + can't start with MRR/MRT
        + TODO1 need to change mlrsearch initial search phase(s)
  + seq-2
    * new ec2 instances
      - add arm instances
      - efa vs ena dpdp
  + seq-3
    - new intel icx

- nic compatibility
  + seq-1
    * fvl nic
      - TODO VPP-1995 "VPP DPDK i40e (FVL NICs) can't initialize VF interface with configured VLAN (fvl api: vlan_stripping_v2)".
  + seq-2
    * fvl nic
      - TODO update compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-iavf-vf, dpdk-i40e-pf vpp tests, for current CSIT environment
  + seq-3
    * mlx nic
      - TODO update compatibility matrix for vpp-rdma, dpdk-mlx5-vf, dpdk-mlx5-pf vpp tests, for current CSIT environment
  + seq-4
    * cvl nic
      - TODO update compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-iavf-vf, dpdk-ice-pf vpp tests, for current CSIT environment

# sut infra hw

- icx testbeds
  + new hw: 2p100ge nic mlx connectx5, commission, once ordered, shipped and delivered
  + new hw: 2n-icx, 3n-icx, build and commission, once shipped & delivered

- ampere n1 testbeds
  + new hw: 3n-alt, build and commission, once shipped & delivered
  + supply mlx connectx5

- dnv testbeds
  + mode: best effort support

- skx testbeds
  + without change

- zn2 testbeds
  + without change

- fvl nic
  + fw, driver compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-i40e-vf, dpdk-i40e-pf vpp tests
  + driver change management
    * kernel driver changes
    * dpdk version change
    * ubuntu or linux kernel version change

- cvl nic
  + fw, driver compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-iavf-vf, dpdk-ice-pf vpp tests
  + driver change management
    * kernel driver changes
    * dpdk version change
    * ubuntu or linux kernel version change

- mlx nic
  + fw, driver compatibility matrix for vpp-rdma, dpdk-mlx5-vf, dpdk-mlx5-pf vpp tests
  + driver change management
    * kernel driver changes

# tg infra

- clx testbeds
  + replace cvl with 2p100ge nic mlx connectx5

# sut and tg infra config

- sut and tg config
  + seq-1
    * hugepages
      - today, 2 MB; experiments, 1 GB
      - TODO investigate no noticeable difference, telemetry analysis to be done
  + seq-2
    * core frequency
      - TODO shall we switch to all-core-turbo
  + seq-3
    * vpp in container
      - TODO calibration and versioning strategy
  + seq-4
    * vpp in VM
      - TODO calibration and versioning strategy
    * testpmd/l3fwd in VM
      - TODO calibration and versioning strategy

## sut aws ec2

- c5n 4xl
  + mlrsearch with mrr triggering reaching admin rate limit
    * need solution from Vratko
    * e.g. replace first mrr trials with exponential search instead
  + ec2 telemetry reporting
    * pkt drop reasons
      - per trial
      - per mlrsearch test duration
    * e.g. limit exceeded
      - pps
      - Gbps
      - else?

- c6gn 4xl
  + patch ready for test
  + consider only after cleaning c5n 4xl

# tg infra config

- seq-1: calibration for STL
  + vpp in l2xc config
  + performance consistency
    * TODO Calibrate: 64B, 78B
    * Calibrate TBD: IMIX 7 : 4 : 1, 1518B : 570B : (64B | 78B)
    * Calibrate not needed: 1518B
    * TO DISCUSS calibrate Jumbo frame
  + tx duration stretching handling
    * detection
    * optimizations
      - trex code
      - trex api's
      - csit code
  + rx in-flight handling
  + trex loop tests
    * clx 100 GbE MLX5
    * icx 100 GbE MLX5
  + ramp-up phase handling

- seq-2: calibration for ASTF
  + performance consistency
  + tcp
    * 64B
    * file transfers?
  + udp
    * 64B
    * file transfers?
  + pcap
    * TODO examples from trex repo?
  + trex loop tests
    * clx 25 GbE FVL
    * icx 100 GbE CVL
  + trex vpp-ip4 tests

- seq-3: performance
  + 100 GbE MLX
    * STL only
    * number of threads
    * thread allocation to trex tasks
      - rx
      - tx
      - latency
      - TODO else?
  + 10 GbE, 25 GbE FVL
    * STL and ASTF
  + 100 GbE CVL - future

- seq-4: central scapy-to-pcap script repository
  + TODO make a proposal

# telemetry

- seq-1: vpp telemetry
  + identify useful telemetry commands/outputs
    * TODO2 cleanup and implement new bundles
- seq-2: linux telemetry
  + identify useful telemetry commands/outputs
    * TODO1 implement new bundles


# ubuntu 22.04

- seq-1: nomad
  + nomad backend
    * TODO1 reinstall host to 22.04  // rls2206 plan
    * TODO2 nomad version bump       // rls2206 plan
- seq-2: containers
  + jjb containers
    * TODO add 22.04
- seq-3: jobs
  + jenkins jobs
    * TODO add 22.04
- seq-4: csit
  + run vpp_device
    * TODO debug 22.04
  + run vpp_perf