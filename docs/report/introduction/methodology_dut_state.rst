DUT state considerations
------------------------

This page discusses considerations for Device Under Test (DUT) state.
DUTs such as VPP require configuration, to be provided before the aplication
starts (via config files) or just after ist starts (via API or CLI access).

During operation DUTs gather various telemetry data, depending on configuration.
This this internal state handling is part of normal operation,
so any performance inpact is included in the test results.
Accessing telemetry data is additional load on DUT,
so we are not doing that in main trial measurements that affect results,
but we include separate trials specifically for gathering runtime telemetry.

But there is one mode class of state that needs specific handling.
Some DUT state is created based on incoming traffic, it affects how DUT handles
the traffic, and (unlike telemetry counters) has uneven impact on CPU load.
Typical example is NAT where opening sessions takes more CPU than
forwarding packet on existing sessions.
We call DUT confgrations with this kind if state "stateful",
and configurations without them "stateless".
(Even though stateless configurations contain state described in previous
paragraphs, and some configuration items may have "stateful" in their name,
such as stateful ACLs.)

Stateful DUT configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, traffic can have two modes of CPU impact.
First packets causing DUT state to change have higher impact,
subsequent packets fitting that state have lower impact.

From performance point of view, this is similar to traffic phases
for stateful protocols, see
`NGFW draft <https://tools.ietf.org/html/draft-ietf-bmwg-ngfw-performance-05#section-4.3.4>`.
In CSIT we borrow the terminology (even if it does not fit perfectly,
see discussion below). Ramp-up traffic causes the state change,
sustain traffic does not change the state.

As the performance is different, each test has to choose which traffic
it wants to test, and manipulate the DUT state to achieve the intended impact.

Ramp up trial
_____________

Tests aiming at sustain performance need to make sure DUT state is created.
We achieve this via a trial, specific purpose of which is to create the state.
Subsequent trials need no specific handling, as state remains the same.

For the state to be set completely, it is important DUT (nor TG) loses
no packets, we achieve this by setting TPS to low enough value.

It is also important each state-affecting packet is sent.
For size-limited traffic profile it is guaranteed by the size limit.
For continuous traffic, we sent long enough duration (based on TPS).

At the end of the ramp up trial, we check telemetry to confirm
the state has been created as expected.
Test fails if the state is not complete.

State Reset
___________

Tests aiming at ramp-up performance do not use ramp-up trial,
and they need to reset the DUT state before each trial measurement.
The way of resetting the state depends on test,
usuall an API call is used to partially de-configure
the part that holds the state, and then re-configure it back.

In CSIT we control the DUT state behavior via a test variable "resetter".
If it is not set, DUT state is not reset.
If it is set, each search algorithm (including MRR) will invoke it
before any trial measuremen (both main and telemetry ones).
Any configuration keyword enabling a feature with DUT state
will check whether a test variable for ramp up (duration) is present.
If it is present, resetter is not set.
If it is not present, the keyword sets the apropriate resetter value.
This logic makes sure either ramp-up or state reset are used.

TODO: Classify trials to main an telemetry in a separate place.

Notes: If both ramp-up and state reser were used, the DUT behavior
would be identical to just reset, while test would take longer to execute.
If neither were ised, DUT will show different performance in subsequent trials,
violating assumptions of search algorithms.

DUT versus protocol ramp-up
___________________________

There are at least three different causes for bandwidth possibly increasing
within a single measurement trial.

First is DUT switching from state modification phase to constant phase,
it is the primary focus of this document.
Using ramp-up traffic before main trials eliminates this cause
for tests wishing to measure the performance of the next phase.
Using size-limited profiles eliminates the next phase
for tests withing to measure performance of this phase.

Second is protocol such as TCP ramping up their throughput to utilize
the bandwidth available. This is the original meaning of "ramp up"
in the IETF draft. In existing tests we are not distinguishing
such phases, trial measurment reports the telemetry from the whole trial
(e.g. throughput is time averaged value).

Third is TCP increasing throughput due to retransmissions triggered by
packet loss. In CSIT we currently try to avoid this behavior
by using small enough data to transfer, so overlap of multiple transactions
(primary cause of packet loss) is unlikely.
But in MRR tests packet loss is stil probable.
Once again, we rely on using telemetry from the whole trial,
resulting in time averaged throughput values.

Stateless DUT configuratons
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are simply configuration which do not set any resetter value
even if ramp-up duration is not configured.
Majority of existing tests are of this type, using continuous traffic profiles.

In order to identify limits of Trex performance,
we have added suites with stateless DUT configuration (VPP ip4base)
subjected to size-limited ASTF traffic.
The discovered throughput server as a basis of comparison
for evaluating result of stateful DUT configurations (VPP NAT)
subjected to the same traffic profile.

DUT versus TG state
~~~~~~~~~~~~~~~~~~~

Traffic Generator profiles can me stateful (ASTF) or stateless.
DUT configuration can be stateful or stateless (with respect to traffic).

In CSIT we currently use all four possible configurations:

- Regular stateless VPP tests use stateless traffic profiles.

- Stateless VPP configuration with stateful profile is used as comparison base.

- Some stateful DUT configurations (NAT44DET, NAT44ED unidirectional)
  are tested using stateless traffic profiles.

- The rest of stateful DUT configurations (NAT33ED bidirectional)
  are tested using stateful traffic profiles.
