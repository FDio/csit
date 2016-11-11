FIB 2.0 Convergence
===================

High level description
----------------------

Definitions:

- "IGP" routes - routes with direct next-hop, i.e. neighbour on a locally
  connected interface.
- "BGP" routes - routes with indirect next-hop, i.e. "IGP" route.
- FIB convergence time calculated as a function of pkt loss:
    - fib_cvg_time = 2 * pkt_loss / pkt_rate [s; pkts, pkts/s]
    - Assumes linear FIB convergence, equal time to update each FIB entry.
- Measurement packets-per-second rate
    - PPS rate at best 100x or 10x higher than FIB size, minimum equal to FIB
      size.
    - the higher the rate, the better measurement resolution.
    - stay withing deterministic zero-loss throughput range, NDR.
- All tests with VPP configured with one ingress and two egress ports
    - all ports connected to TG.

Test descriptions:

1. IGP convergence
    a) program <N> "IGP" routes pointing to egress ports:
        - each with 2 unequal paths via different neighbours.
    b) start pkt traffic:
        - hit all "IGP" FIB entries.
        - increment destination IP address within FIB range of <N> "IGP" routes.
    c) shut port used for primary (lower cost) path.
        -  packets should get re-routed to secondary (higher cost) path.
    d) measure packet loss
        - calculate amount of time during which packet loss occurred.
    e) test values of <N> = 10, 1k, 10k.
2. BGP PIC-core:
    a) program <M> "BGP" routes, each with one path via "IGP" route
        - "IGP" route as indirect next-hop.
        - "IGP" route programmed with "primary" direct next-hop.
    b) start pkt traffic:
        - hit all "BGP" FIB entries.
        - increment destination IP address within FIB range of <M> "BGP" routes.
    c) re-program the direct next-hop for "IGP" route to secondary direct
       next-hop.
        - packets should get re-routed to secondary direct next-hop.
    d) measure packet loss.
        - calculate amount of time during which packet loss occurred.
    e) test values of M = 10, 100k, 1M; N = 1, 10.
    f) variation of 2.a.
        - program "IGP" route with 2 next-hops (2 interfaces)
        - run traffic
        - shut down one interface
        - should see zero or close-to-zero packet loss
3. iBGP PIC Edge:
    a) program <M> "BGP" routes, each with two paths via "IGP" routes
        - "IGP" route as indirect next-hop.
        - each "IGP" route with different direct next-hop, locally connected
          neighbour.
    b) start pkt traffic:
        - hit all "BGP" FIB entries.
        - increment destination IP address within FIB range of <M> "BGP" routes.
    c) delete one of the "IGP" routes.
    d) measure packet loss.
        - calculate amount of time during which packet loss occurred.
    e) test values of M = 10, 100k, 1M; N = 1, 10.
4. eBGP-PIC-edge:
    a) program <M> BGP routes, each with two paths via 2 different direct
       next-hops.
    b) start pkt traffic:
        - hit all "BGP" FIB entries.
        - increment destination IP address within FIB range of <M> "BGP" routes.
    c) shut one interface.
    d) measure packet loss.
        - calculate amount of time during which packet loss occurred.
    e) test values of M = 10, 100k, 1M.


Low Level Description
---------------------

1. IGP Convergence

[Top] TG-DUT1-DUT2-TG
      VLAN sub-ifs created on interfaces between DUTs
      TG_if1 -> DUT1_if1 -> (DUT1_if2_sub1 -> DUT2_if1_sub1 AND DUT1_if2_sub2 ->
      DUT2_if1_sub2) -> DUT2_if2

[Cfg] 1. DUT configuration (traffic is sent in one direction):
         - Create two sub-interfaces on the physical interface directly
           connected to the other DUT. The sub-interfaces have two different
           VLAN IDs.
         - Set the IP addresses on interface connected to TG and on both
           sub-interfaces, do not set IP on the super-interface.
         - Set all used interfaces and sub-interfaces up.
         - Add neighbours to interface connected to TG and both sub-interfaces.
         - DUT1: Add routes to route traffic via both sub-interfaces in the used
           direction (from TG to DUT2).
           DUT2: Add routes to route traffic via interface connected to TG.
      2. Number of routes used in tests:
         - 10, 1k, 10k, 100k, 1M
      3. Traffic:
         - Use NDR, 3Mpps for all numbers of routes.
         - Traffic sent in one direction.

[Ver] Find the time of FIB2.0 Convergence:
      - Start the traffic generator,
      - Set down the sub-interface used for primary path.
      - Stop the traffic generator.
      - Get the number of lost packets.
      - Evaluate the convergence time:
        fib_cvg_time = 2 * pkt_loss / pkt_rate [s; pkts, pkts/s]
      - Repeat for all number of routes.
