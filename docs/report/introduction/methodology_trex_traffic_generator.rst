TRex Traffic Generator
----------------------

Usage
~~~~~

`TRex traffic generator <https://trex-tgn.cisco.com>`_ is used for majority
CSIT performance tests. TRex stateless mode is used to measure NDR and PDR
throughputs using MLRsearch and to measure maximum transfer rate in MRR tests.

TRex is installed and run on the TG compute node. The typical procedure is:

- If the TRex is not already installed on TG, please refer to
  `TRex installation`_.
- TRex configuration is set in its configuration file
  ::

  $ sudo -E -S sh -c 'cat << EOF > /etc/trex_cfg.yaml
  - version: 2
    c: 15
    limit_memory: 8192
    interfaces: ["${pci1}","${pci2}"]
    port_info:
      - dest_mac: [${dest_mac1}]
        src_mac: [${src_mac1}]
      - dest_mac: [${dest_mac2}]
        src_mac: [${src_mac2}]
    platform :
      master_thread_id: 0
      latency_thread_id: 16
      dual_if:
          - socket: 0
            threads: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
  EOF'

- TRex is started in the interactive mode as a background service
  ::

  $ sh -c 'cd <t-rex-install-dir>/scripts/ && \
    sudo nohup ./t-rex-64 -i --prefix $(hostname) --hdrh --no-scapy-server \
    > /tmp/trex.log 2>&1 &' > /dev/null

- There are traffic streams dynamically prepared for each test, based on traffic
  profiles. The traffic is sent and the statistics obtained using API
  :command:`trex.stl.api.STLClient`.

Measuring Packet Loss
~~~~~~~~~~~~~~~~~~~~~

Following sequence is followed to measure packet loss:

- Create an instance of STLClient.
- Connect to the client.
- Add all streams.
- Clear statistics.
- Send the traffic for defined time.
- Get the statistics.

If there is a warm-up phase required, the traffic is sent also before
test and the statistics are ignored.

Measuring Latency
~~~~~~~~~~~~~~~~~

If measurement of latency is requested, two more packet streams are
created (one for each direction) with TRex flow_stats parameter set to
STLFlowLatencyStats. In that case, returned statistics will also include
min/avg/max latency values and encoded HDRHistogram data.
