# sut infra hw

 - icx testbeds
   - new hw: 2p100ge nic mlx connectx5, commission, once ordered, shipped and delivered
   - new hw: 2n-icx, 3n-icx, build and commission, once shipped & delivered

 - ampere n1 testbeds
   - new hw: 3n-amp, build and commission, once shipped & delivered
   - supply mlx connectx5

 - dnv testbeds
   - mode: best effort support

 - skx testbeds
   - without change

 - zn2 testbeds
   - without change

 - fvl nic
   - fw, driver compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-i40e-vf, dpdk-i40e-pf vpp tests
   - driver change management
     - kernel driver changes
     - dpdk version change
     - ubuntu or linux kernel version change

 - cvl nic
   - fw, driver compatibility matrix for vpp-af-xdp, vpp-avf, dpdk-ice-vf, dpdk-ice-pf vpp tests
   - driver change management
     - kernel driver changes
     - dpdk version change
     - ubuntu or linux kernel version change

 - mlx nic
   - fw, driver compatibility matrix for vpp-rdma, dpdk-mlx5-vf, dpdk-mlx5-pf vpp tests
   - driver change management
     - kernel driver changes

# tg infra

 - clx testbeds
   - replace cvl with 2p100ge nic mlx connectx5

# sut infra config

 - hugepages
   - today, 2 MB
   - experiments, 1 GB
   - no noticeable difference in throughput
   - telemetry analysis to be done

 - core frequency
   - shall we switch to all-core-turbo ?

## sut with containers

 - vpp in container
 - calibration and versioning strategy

## sut with VMs

 - vpp in VM
 - testpmd/l3fwd in VM
 - calibration and versioning strategy

## sut aws ec2

 - c5n 4xl
   - mlrsearch with mrr triggering reaching admin rate limit
     - need solution from Vratko
     - e.g. replace first mrr trials with exponential search instead
   - ec2 telemetry reporting
     - pkt drop reasons
       - per trial
       - per mlrsearch test duration
     - e.g. limit exceeded
       - pps
       - Gbps
       - else?

 - c6gn 4xl
   - patch ready for test
   - consider only after cleaning c5n 4xl

# tg infra config

 - calibration for STL
   - performance consistency
     - 64B, 78B
     - IMIX 7 : 4 : 1, 1518B : 570B : (64B | 78B)
     - 1518B
     - Jumbo frame calibration
   - tx duration stretching handling
     - detection
     - optimizations
       - trex code
       - trex api's
       - csit code
   - rx in-flight handling
   - trex loop tests
     - clx 25 GbE FVL
     - icx 100 GbE CVL
   - ramp-up phase handling

 - calibration for ASTF
   - performance consistency
   - tcp
     - 64B
     - file transfers?
   - udp
     - 64B
     - file transfers?
   - pcap
     - TODO examples from trex repo?
   - trex loop tests
     - clx 25 GbE FVL
     - icx 100 GbE CVL
   - trex vpp-ip4 tests

 - central scapy-to-pcap script repository

 - performance
   - 100 GbE MLX
     - STL only
     - number of threads
     - thread allocation to trex tasks
       - rx
       - tx
       - latency
       - TODO else?
   - 10 GbE, 25 GbE FVL
     - STL and ASTF
   - 100 GbE CVL - future

# telemetry

 - vpp interface counters
   - show hw verbose
   - show interface
   - TODO complete the list

 - vpp memory
   - show memory
   - show fib memory
   - show physmem

 - vpp perfmon
   - incl. `show runtime`

 - linux telemetry

# ubuntu 22.04

 - perf
   - slow rollout (fmlm - first machine, last machine)

 - backend
   - nomad infra
   - nomad version bump

 - containers
   - add 22.04

 - jenkins
   - add jobs

 - csit
   - bump python
   - bump pypi
   - debug
