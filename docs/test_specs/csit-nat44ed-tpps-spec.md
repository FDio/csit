## Content

<!-- MarkdownTOC autolink="true" -->

- [Tests for NAT44-ED](#tests-for-nat44-ed)
- [TPPS Test Objectives](#tpps-test-objectives)
- [Input Parameters](#input-parameters)
- [TRex ASTF Program for TPPS](#trex-astf-program-for-tpps)
- [UDP Measurements](#udp-measurements)
  - [TRex Packet and Traffic Counters](#trex-packet-and-traffic-counters)
  - [TRex Error Counters](#trex-error-counters)
  - [VPP Packet and Session Counters](#vpp-packet-and-session-counters)
  - [VPP Error Counters](#vpp-error-counters)
- [TCP Measurements](#tcp-measurements)
  - [TRex Packet and Traffic Counters](#trex-packet-and-traffic-counters-1)
  - [TRex Error Counters](#trex-error-counters-1)
  - [VPP Packet and Session Counters](#vpp-packet-and-session-counters-1)
  - [VPP Error Counters](#vpp-error-counters-1)
- [TPPS Methodology](#tpps-methodology)
  - [MRR](#mrr)
  - [NDRPDR](#ndrpdr)

<!-- /MarkdownTOC -->

## Tests for NAT44-ED

Two types of tests are developed for NAT44-ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Calls-Per-Second, CPS
- Transactions-Per-Second, TPS(?)
  - Does it make sense to have a separate CPS and TPS, with CPS being a
    special case of TPS, with just connect and close phases?
- Transaction-Packets-Per-Second, TPPS

Both test types are to be executed separately per each L4 protocol:
TCP/IP and UDP.

This note describes CPS.

## TPPS Test Objectives

Discover DUT's highest sustained transaction data packet throughput rate
across NAT44ED 5-tuple stateful session entries, following their
creation.

Transaction data packet throughput rate is discovered for TCP (and UDP)
data packets exchanged between client and server side for each
connection, after connection establishment.

For specific number of TCP (or UDP) sessions, the data packet rate is
govern by the number of transactions per second and amount of data to be
transmitted for each transaction.

Different frame sizes are tested similarly to stateless throughput
tests. Initial tests are focusing on symmetric data exchange, with
client and server transmitting the same amount of data packets to each
other.

Similarly to packet throughput, three TPPS rates are discovered:

- TPPS-MRR, TPPS maximum received rate, regardless of packet loss.
- TPPS-NDR, TPPS non-drop rate, with zero packet loss.
- TPPS-PDR, TPPS partial drop rate, with configured packet loss ratio.

## Input Parameters

- tps_rate, rate of transactions to be used by traffic generator,
  limited by traffic generator capabilities, Ethernet link(s) rate and
  NIC model. The same rate is used to established connections.
- client_data_pkt_multiplier, number of data packets transmitted by
  client per transaction.
- server_data_pkt_multiplier, number of data packets transmitted by
  server per transaction.
- max_session_number, maximum number of sessions to be established and
  tested.
- packet_loss_ratio, maximum acceptable PLR search criteria for PDR
  measurements.
- final_relative_width, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.
- TRex ASTF program, defining the TPPS transaction per L4 protocol
  tested, including connect sequence (TCP, UDP), delay, data exchange,
  delay, close sequence, delay. Delay phases are required to account for
  successfully established and closed sessions with associated packet
  and session counters.

## TRex ASTF Program for TPPS

TRex ASTF program defines following transactions for separate TCP and
UDP tests:

- TPPS with TCP
  - connect(syn,syn-ack,ack),
    - pkts client tx 2, rx 1
    - pkts server tx 1, rx 2
  - delay,
    - no packets
  - data_send(c2s-pkts,s2c-pkts)
    - pkts client tx c2s-pkts, rx s2c-pkts
    - pkts server tx s2c-pkts, rx c2s-pkts
  - delay,
    - no packets
  - close(fin,fin-ack,ack,ack)
    - pkts client tx 2, rx 2
    - pkts server tx 1, rx 2
  - delay,
    - no packets
- TPPS with UDP
  - connect_and_close(connect-req,connect-ack),
    - pkts client tx 1, rx 1
    - pkts server tx 1, rx 1
  - delay,
    - no packets
  - data_send(c2s-pkts,s2c-pkts)
    - pkts client tx c2s-pkts, rx s2c-pkts
    - pkts server tx s2c-pkts, rx c2s-pkts
  - delay,
    - no packets
  - connect_and_close(close-req,close-ack),
    - pkts client tx 1, rx 1
    - pkts server tx 1, rx 1

TRex ASTF program configuration parameters:

- Limit of sessions, set to max_session_number.
- IPv4 source and destination address and port ranges matching the
  limit of sessions.
  - Source and destination address changing packet-by-packet with two
    separate profiles i) incrementing sequentially pair-wise and ii)
    changed randomly (with seed) pair-wise.
  - Source port changing randomly within the range.
- Multiplier, target number of transactions per second to be executed.
  Multiplier applies to connect, data_send and close phases.
- Number of data packets sent per transaction in each direction, from
  client to server (c2s-pkts) and from server to client (s2c-pkts). On
  the wire data packet rate is govern by the number of data packets per
  transaction times the multiplier.
- Size of data packets, aligned with Ethernet untagged frame sizes used for stateless throughput tests.
  - For TCP: 72B (minimum frame size), 1518B, IMIX(?).
  - For UDP: ??B (minimum frame size), 1518B, IMIX(?).
- Duration of trial, function of max_session_number and trial_cps_rate
  - For TCP: 3 x (max_session_number / trial_cps_rate) + 3 x Delay
  - For UDP: 3 x (max_session_number / trial_cps_rate) + 3 x Delay

## UDP Measurements
### TRex Packet and Traffic Counters
### TRex Error Counters
### VPP Packet and Session Counters
### VPP Error Counters
## TCP Measurements
### TRex Packet and Traffic Counters
### TRex Error Counters
### VPP Packet and Session Counters
### VPP Error Counters
## TPPS Methodology
### MRR
### NDRPDR