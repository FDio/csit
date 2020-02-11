
.. raw:: latex

    \clearpage

.. _network_service_density:

NFV Service Density
===================

NFV Service Density is benchmarked in three distinct NF service
configurations:

- VNF Service Chains Routing
- CNF Service Chains Routing
- CNF Service Pipelines Routing
- VNF Service Chains Tunnels
- CNF Service Chains IPSEC

Each configuration is tested in a number of service density combinations
[Number of Service Instances] x [Number of NFs per Service Instance].
The actual tested range is based on available CPU physical core
resources.

.. toctree::

    cnf_service_chains_ipsec

..
    vnf_service_chains
    cnf_service_chains
    cnf_service_pipelines
    vnf_service_chains_vxlan
