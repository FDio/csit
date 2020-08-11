## Content

<!-- MarkdownTOC autolink="true" -->

- [Tests for NAT44-ED](#tests-for-nat44-ed)
- [CPS Test Objectives](#cps-test-objectives)
- [Input Parameters](#input-parameters)
- [TRex ASTF Program for CPS](#trex-astf-program-for-cps)
- [UDP Measurements and Counters](#udp-measurements-and-counters)
  - [UDP TRex Packets and Sessions](#udp-trex-packets-and-sessions)
  - [UDP TRex Errors](#udp-trex-errors)
  - [UDP VPP Packets and Sessions](#udp-vpp-packets-and-sessions)
  - [UDP VPP Errors](#udp-vpp-errors)
- [TCP Measurements and Counters](#tcp-measurements-and-counters)
  - [TCP TRex Packets and Sessions](#tcp-trex-packets-and-sessions)
  - [TCP TRex Errors](#tcp-trex-errors)
  - [TCP VPP Packets and Sessions](#tcp-vpp-packets-and-sessions)
  - [TCP VPP Errors](#tcp-vpp-errors)
- [CPS Methodology](#cps-methodology)
  - [CPS-MRR](#cps-mrr)
  - [CPS-NDRPDR](#cps-ndrpdr)

<!-- /MarkdownTOC -->

## Tests for NAT44-ED

Two types of tests are developed for NAT44-ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Calls-Per-Second, CPS
- Transactions-Per-Second, TPS

Both test types are to be executed separately per each L4 protocol:
TCP/IP and UDP.

This note describes CPS.

## CPS Test Objectives

Discover DUT's highest sustain rate of creating fully functional NAT44ED
5-tuple stateful session entries. Session entry is considered fully
functional, if packets associated with this entry are NAT44ED processed
and forwarded in both directions without loss.

Similarly to packet throughput, three CPS rates are discovered:

- CPS-MRR, maximum received rate for CPS, regardless of packet loss.
- CPS-NDR, non-drop rate for CPS, with zero packet loss.
- CPS-PDR, partial drop rate for CPS, with configured packet loss ratio.

## Input Parameters

- max_cps_rate, maximum rate of establishing connections, to be used by
  traffic generator, limited by traffic generator capabilities, Ethernet
  link(s) rate and NIC model.
- min_cps_rate, minimum rate of establishing connections to be used for
  measurements. Search fails if lower transmit rate needs to be used to
  meet search criteria.
- max_session_number, maximum number of sessions to be established and
  tested.
- packet_loss_ratio, maximum acceptable PLR search criteria for PDR
  measurements.
- final_relative_width, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.
- TRex ASTF program, defining the CPS transaction per L4
  protocol tested, including connect sequence (TCP, UDP), delay, close
  sequence, delay. Delay phases are required to account for successfully
  established and closed sessions with associated packet and session
  level counters.

## TRex ASTF Program for CPS

TRex ASTF program defines following transactions for separate TCP and
UDP tests:

- CPS with TCP
  - connect(syn,syn-ack,ack),
    - pkts client tx 2, rx 1
    - pkts server tx 1, rx 2
  - delay,
    - no packets
  - close(fin,fin-ack,ack,ack)
    - pkts client tx 2, rx 2
    - pkts server tx 1, rx 2
- CPS with UDP
  - connect_and_close(req,ack),
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
- Multiplier, target number of transactions per second to be executed. Multiplier applies to connect and close phases.
- Duration of trial, function of max_session_number and trial_cps_rate
  - For TCP: 2 x (max_session_number / trial_cps_rate) + 2 x Delay
  - For UDP: (max_session_number / trial_cps_rate) + Delay

## UDP Measurements and Counters

TRex counters polled every set interval (1 sec?).

### UDP TRex Packets and Sessions

```
#### Statistics #####
{
  "1.0088909808546305": {
    "0": {
      "opackets": 57481, ****
      "ipackets": 57440, ****
    },
    "1": {
      "opackets": 57440, ****
      "ipackets": 57481, ****
    },
    "traffic": {
      "client": {
        "m_active_flows": 73, ****
        "m_est_flows": 73, ****
        "udps_connects": 57513, ****
        "udps_closed": 57440, ****
        "udps_sndpkt": 57513, ****
        "udps_rcvpkt": 57440 ****
      },
      "server": {
        "udps_accepts": 57481, ****
        "udps_closed": 57481, ****
        "udps_sndpkt": 57481, ****
        "udps_rcvpkt": 57481 ****
      }
  }

**** action counter
---- ignore counter
```

Actioned counters:

- Packet loss calculations
  - "opackets"
  - "ipackets"
- Session integrity calculations
  - "udps_*"
- To be analysed
  - "m_active_flows"
  - "m_est_flows"

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### UDP TRex Errors

```
  "traffic": {
    "client": {
      "udps_keepdrops": 26713, ****
      "err_rx_throttled": 2 ----
      "err_c_nf_throttled": 2285312, ****
      "err_flow_overflow": 3563 ****
    },
    "server": {
      "err_rx_throttled": 1 ****
    }
  }

**** action error
---- ignore error
```

Actioned errors:

- "udps_keepdrops", TRex out of capacity, dropping UDP KAs(?)
- "err_c_nf_throttled", TRex out of capacity, throttling workers(?)
- "err_flow_overflow", unknown flow(?)

Ignored errors:
- "err_rx_throttled", TRex rx worker throttled down.

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### UDP VPP Packets and Sessions

- VPP show nat44 summary

  ```
  max translations per thread: 81920
  max translations per user: 81920
  total timed out sessions: 0
  total sessions: 64514
  total tcp sessions: 0
  total tcp established sessions: 0
  total tcp transitory sessions: 0
  total tcp transitory (WAIT-CLOSED) sessions: 0
  total tcp transitory (CLOSED) sessions: 0
  total udp sessions: 64514
  total icmp sessions: 0
  ```

- VPP show interface

  ```
  <TODO add sample output>
  ```

- VPP show runtime

  ```
  <TODO add sample output>
  ```

### UDP VPP Errors

- VPP show errors

  ```
  Count                    Node                  Reason
       32258       nat44-in2out-worker-handoff      same worker
       32256       nat44-in2out-worker-handoff      do handoff
       32258             nat44-ed-out2in            good out2in packets processed
       32258             nat44-ed-out2in            UDP packets
       32258        nat44-ed-in2out-slowpath        good in2out packets processed
       32258        nat44-ed-in2out-slowpath        UDP packets
       32256       nat44-out2in-worker-handoff      same worker
       32258       nat44-out2in-worker-handoff      do handoff
       32256             nat44-ed-out2in            good out2in packets processed
       32256             nat44-ed-out2in            UDP packets
       32256        nat44-ed-in2out-slowpath        good in2out packets processed
       32256        nat44-ed-in2out-slowpath        UDP packets
  ```

## TCP Measurements and Counters

TRex counters polled every set interval (1 sec?).

### TCP TRex Packets and Sessions

```
#### Statistics #####
{
  "1.0088909808546305": {
    "0": {
        "opackets": 14338, ****
        "ipackets": 7169, ****
    },
    "1": {
        "opackets": 7169, ****
        "ipackets": 14338, ****
    "traffic": {
        "client": {
            "m_active_flows": 7185, ****
            "m_est_flows": 7169, ****
            "tcps_connattempt": 7185, ****
            "tcps_connects": 7169, ****
            "tcps_segstimed": 7185, ****
            "tcps_rttupdated": 7169, ****
            "tcps_sndtotal": 14354, ****
            "tcps_sndctrl": 7185, ****
            "tcps_sndacks": 7169 ****
        },
        "server": {
            "m_active_flows": 7177, ****
            "m_est_flows": 7161, ****
            "tcps_accepts": 7177, ****
            "tcps_connects": 7161, ****
            "tcps_segstimed": 7177, ****
            "tcps_rttupdated": 7161, ****
            "tcps_sndtotal": 7177, ****
            "tcps_sndacks": 7177, ****
            "tcps_rcvackpack": 7161, ****
        }
      }
  },
},
**** action counter
---- ignore counter
```

Actioned counters:

- Packet loss calculations
  - "opackets"
  - "ipackets"
- Session integrity calculations
  - "udps_*"
- To be analysed
  - "m_active_flows"
  - "m_est_flows"

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### TCP TRex Errors

```
  "traffic": {
      "client": {
          "tcps_sndwinup": 26512,
          "err_rx_throttled": 6551
      },
      "server": {
          "tcps_sndwinup": 35818,
          "tcps_rcvdupack": 64512,
          "err_rx_throttled": 12724
      }

**** action error
---- ignore error
```

Actioned errors:

- "tcps_sndwinup", window update-only packets sent

Ignored errors:
- "err_rx_throttled", TRex rx worker throttled down.

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### TCP VPP Packets and Sessions

- VPP show nat44 summary

  ```
  <TODO add sample output>
  ```

- VPP show interface

  ```
  <TODO add sample output>
  ```

- VPP show runtime

  ```
  <TODO add sample output>
  ```

### TCP VPP Errors

- VPP show errors

  ```
  Count                    Node                  Reason
       32258       nat44-in2out-worker-handoff      same worker
       32256       nat44-in2out-worker-handoff      do handoff
       32258             nat44-ed-out2in            good out2in packets processed
       32258             nat44-ed-out2in            UDP packets
       32258        nat44-ed-in2out-slowpath        good in2out packets processed
       32258        nat44-ed-in2out-slowpath        UDP packets
       32256       nat44-out2in-worker-handoff      same worker
       32258       nat44-out2in-worker-handoff      do handoff
       32256             nat44-ed-out2in            good out2in packets processed
       32256             nat44-ed-out2in            UDP packets
       32256        nat44-ed-in2out-slowpath        good in2out packets processed
       32256        nat44-ed-in2out-slowpath        UDP packets
  ```

## CPS Methodology

### CPS-MRR

### CPS-NDRPDR
