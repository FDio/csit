AWS Performance Testbeds
------------------------

CSIT implements two virtual machine topology types running in AWS EC2:

- **2-Node Topology**: Consists of one EC2 instance as a System Under
  Test (SUT) and one EC2 instance acting as a Traffic Generator
  (TG), with both instances connected into a ring topology. Used for
  executing tests that require frame encapsulations supported by TG.

- **3-Node Topology**: Consists of two EC2 instances acting as a Systems
  Under Test (SUTs) and one EC2 instance acting as a Traffic Generator
  (TG), with all instances connected into a ring topology. Used for
  executing tests that require frame encapsulations not supported by TG
  e.g. certain overlay tunnel encapsulations and IPsec.

AWS EC2 Instances
----------------

CSIT is using AWS EC2 C5n instances as System Under Test and TG virtual
machines. C5n instances got selected to take advantage of high network
throughput and packet rate performance. C5n instances offer up to 100
Gbps network bandwidth and increased memory over comparable C5
instances. For more information, see
`Instance types <https://aws.amazon.com/ec2/instance-types/>`_.

C5n features:

- 3.0 GHz Intel Xeon Platinum (Skylake) processors with Intel AVX-512
  instructions.
- Sustained all core Turbo frequency of up to 3.4GHz, and single core
  turbo frequency of up to 3.5 GHz.
- Requires HVM AMIs (Amazon Machine Images) that include drivers for ENA
  and NVMe. See :ref:`csit_ami` for more information.
- Network bandwidth to up to 100 Gbps.
- Powered by the AWS Nitro System, a combination of dedicated hardware
  and lightweight hypervisor.

+-------------+------+--------------+------------------------+-----------------------------+----------------------+
| Model       | vCPU | Memory (GiB) | Instance Storage (GiB) | Network Bandwidth (Gbps)*** | EBS Bandwidth (Mbps) |
+=============+======+==============+========================+=============================+======================+
|c5n.large    |    2 |         5.25 |        EBS-Only        |                    Up to 25 |          Up to 4,750 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.xlarge   |    4 |        10.5  |        EBS-Only        |                    Up to 25 |          Up to 4,750 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.2xlarge  |    8 |        21    |        EBS-Only        |                    Up to 25 |          Up to 4,750 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.4xlarge  |   16 |        42    |        EBS-Only        |                    Up to 25 |                4,750 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.9xlarge  |   36 |        96    |        EBS-Only        |                          50 |                9,500 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.18xlarge |   72 |       192    |        EBS-Only        |                         100 |               19,000 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+
|c5n.metal    |   72 |       192    |        EBS-Only        |                         100 |               19,000 |
+-------------+------+--------------+------------------------+-----------------------------+----------------------+

CSIT is configured by default to use `c5n.4xlarge` in `eu-central-1` AWS
region due to allocation stability issues with `c5n.9xlarge` in
`eu-central-1` region.


AWS EC2 Networking
------------------

CSIT EC2 instances are equipped with AWS Elastic Network Adapter
(ENA) supporting AWS enhanced networking. Enhanced networking uses
single root I/O virtualization (SR-IOV) to provide high-performance
networking capabilities. For more information, see 
`Elastic Network Adapter <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking-ena.html>`_.

For more information about the current advertised AWS ENA performance
limits, see
`Computed optimized instances <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/compute-optimized-instances.html>`_.

CSIT DUTs make use of AWS ENA DPDK driver supplied by AWS and specified
in
`amzn drivers dpdk <https://github.com/amzn/amzn-drivers/tree/master/userspace/dpdk>`_.
