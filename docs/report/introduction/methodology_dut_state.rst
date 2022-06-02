DUT state considerations
------------------------

This page discusses considerations for Device Under Test (DUT) state.
DUTs such as VPP require configuration, to be provided before the aplication
starts (via config files) or just after it starts (via API or CLI access).

During operation DUTs gather various telemetry data, depending on configuration.
This internal state handling is part of normal operation,
so any performance impact is included in the test results.
Accessing telemetry data is additional load on DUT,
so we are not doing that in main trial measurements that affect results,
but we include separate trials specifically for gathering runtime telemetry.

But there is one kind of state that needs specific handling.
This kind of DUT state is dynamically created based on incoming traffic,
it affects how DUT handles the traffic, and (unlike telemetry counters)
it has uneven impact on CPU load.
Typical example is NAT, where detecting new sessions takes more CPU than
forwarding packet on existing (open or recently closed) sessions.
We call DUT configurations with this kind of state "stateful",
and configurations without them "stateless".
(Even though stateless configurations contain state described in previous
paragraphs, and some configuration items may have "stateful" in their name,
such as stateful ACLs.)

Stateful DUT configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, the level of CPU impact of traffic depends on DUT state.
The first packets causing DUT state to change have higher impact,
subsequent packets matching that state have lower impact.

From performance point of view, this is similar to traffic phases
for stateful protocols, see
`NGFW draft <https://tools.ietf.org/html/draft-ietf-bmwg-ngfw-performance-05#section-4.3.4>`.
In CSIT we borrow the terminology (even if it does not fit perfectly,
see discussion below). Ramp-up traffic causes the state change,
sustain traffic does not change the state.

As the performance is different, each test has to choose which traffic
it wants to test, and manipulate the DUT state to achieve the intended impact.

Ramp-up trial
_____________

Tests aiming at sustain performance need to make sure DUT state is created.
We achieve this via a ramp-up trial, specific purpose of which
is to create the state. Subsequent trials need no specific handling,
as the state remains the same.

For the state to be set completely, it is important DUT (nor TG) does not lose
any packets. We achieve this by setting the profile multiplier (TPS from now on)
to low enough value.

It is also important each state-affecting packet is sent.
For size-limited traffic profile it is guaranteed by the size limit.
For continuous traffic, we set a long enough duration (based on TPS).

At the end of the ramp-up trial, we check DUT state to confirm
it has been created as expected.
Test fails if the required state is not (completely) created.

State Reset
___________

Tests aiming at ramp-up performance do not use ramp-up trial,
and they need to reset the DUT state before each trial measurement.
The way of resetting the state depends on test,
usually an API call is used to partially de-configure
the part that holds the state, and then re-configure it back.

In CSIT we control the DUT state behavior via a test variable "resetter".
If it is not set, DUT state is not reset.
If it is set, each search algorithm (including MRR) will invoke it
before all trial measurements (both main and telemetry ones).
Any configuration keyword enabling a feature with DUT state
will check whether a test variable for ramp-up rate is present.
If it is present, resetter is not set.
If it is not present, the keyword sets the apropriate resetter value.
This logic makes sure either ramp-up or state reset are used.

..
    TODO: Classify trials into main and telemetry, in a separate place.

Notes: If both ramp-up and state reset were used, the DUT behavior
would be identical to just reset, while test would take longer to execute.
If neither were used, DUT will show different performance in subsequent trials,
violating assumptions of search algorithms.

DUT versus protocol ramp-up
___________________________

There are at least three different causes for bandwidth possibly increasing
within a single measurement trial.

The first is DUT switching from state modification phase to constant phase,
it is the primary focus of this document.
Using ramp-up traffic before main trials eliminates this cause
for tests wishing to measure the performance of the next phase.
Using size-limited profiles eliminates the next phase
for tests wishing to measure performance of this phase.

The second is protocol such as TCP ramping up their throughput to utilize
the bandwidth available. This is the original meaning of "ramp up"
in the NGFW draft (see above).
In existing tests we are not using this meaning of TCP ramp-up.
Instead we use only small transactions, and large enough initial window
so TCP acts as ramped-up already.

The third is TCP increasing throughput due to retransmissions triggered by
packet loss. In CSIT we again try to avoid this behavior
by using small enough data to transfer, so overlap of multiple transactions
(primary cause of packet loss) is unlikely.
But in MRR tests, packet loss is still expected.

Stateless DUT configuratons
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are simple configurations, which do not set any resetter value
(even if ramp-up duration is not configured).
Majority of existing tests are of this type, using continuous traffic profiles.

In order to identify limits of Trex performance,
we have added suites with stateless DUT configuration (VPP ip4base)
subjected to size-limited ASTF traffic.
The discovered rates serve as a basis of comparison
for evaluating the results for stateful DUT configurations (VPP NAT44ed)
subjected to the same traffic profiles.

DUT versus TG state
~~~~~~~~~~~~~~~~~~~

Traffic Generator profiles can be stateful (ASTF) or stateless (STL).
DUT configuration can be stateful or stateless (with respect to packet traffic).

In CSIT we currently use all four possible configurations:

- Regular stateless VPP tests use stateless traffic profiles.

- Stateless VPP configuration with stateful profile is used as a base for
  comparison.

- Some stateful DUT configurations (NAT44DET, NAT44ED unidirectional)
  are tested using stateless traffic profiles and continuous traffic.

- The rest of stateful DUT configurations (NAT44ED bidirectional)
  are tested using stateful traffic profiles and size limited traffic.
