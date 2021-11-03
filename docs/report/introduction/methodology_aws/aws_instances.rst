Instances
---------

CSIT is using C5n instances for high compute applications that can take
advantage of improved network throughput and packet rate performance. C5n
instances offers up to 100 Gbps network bandwidth and increased memory over
comparable C5 instances [aws_it]_.

Features:

- 3.0 GHz Intel Xeon Platinum processors with Intel Advanced Vector Extension
  512 (AVX-512) instruction set.
- Sustained all core Turbo frequency of up to 3.4GHz, and single core turbo
  frequency of up to 3.5 GHz.
- Requires HVM AMIs that include drivers for ENA and NVMe [aws_ena]_.
- Network bandwidth increases to up to 100 Gbps, delivering increased
  performance for network intensive applications.
- Powered by the AWS Nitro System, a combination of dedicated hardware and
  lightweight hypervisor.

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

CSIT is configured by default to use `c5n.4xlarge` in `eu-central-1` AWS region
due to allocation stability issues with `c5n.9xlarge` in `eu-central-1` region.


AWS Elastic Network Adapter (ENA)
---------------------------------

Enhanced networking uses single root I/O virtualization (SR-IOV) to provide
high-performance networking capabilities on supported instance types. SR-IOV is
a method of device virtualization that provides higher I/O performance and lower
CPU utilization when compared to traditional virtualized network interfaces
[aws_ena]_.

Current advertised limits are captured in [aws_limits]_.

.. [aws_it] `Instance types <https://aws.amazon.com/ec2/instance-types/>`_
.. [aws_ena] `Elastic Network Adapter <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking-ena.html>`_
.. [aws_limits] `<https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/compute-optimized-instances.html>`_