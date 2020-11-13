
Test Bed Considerations
^^^^^^^^^^^^^^^^^^^^^^^

Is it "test bed" or "testbed"?
I assume it means "SUT" plus "test equipment" together,
but is should be clarified.
Maybe it is already defined in some RFC? Then give link.

The whole section is useful.
It would be good to give more details on
"testbed characteristics are stable during the entire test session"
and "testbed reference pre-tests".
Maybe this section can became a standalone RFC?

Not sure about "safety margin of 10%",
I feel different SUTs can have different margins.

Deficiencies
------------

What to to if testbed is not good enough?
What if maximal offered load is unknown?
(I.e. what to do if offered load is different from intended load?)
What if duration stretching happens?
What if there is a variance in offered load
(not caused by TCP but by hardware limitations)?
What if reading counters decreases offered load?
What if generated traffic is "bursty"?

Traffic Load Profile
^^^^^^^^^^^^^^^^^^^^

Sustian phase follows after ramp-up phase immediately,
without any pause, right? Then there is in-flight traffic
at sustain phase start and end, making it hard to get precise counters.
Maybe not an issue for this draft, as they do not do NDR level of strictness,
and failed transactions are tolerated if they are infrequent enough.

Traffic generation
------------------

Test equipment takes some direct input parameters.
Different equipments may take different parameters.
Some other quantities may be controllable.
(If you specify pps and packet size, you know bps.)
But some other quantities may not be controllable directly,
and would require some searching and/or dynamic corrections
to the direct inputs.

For example, the relation between number of active TCP connections
and offered load (pps) depends on SUT latency.
For CSIT, TRex does not directly control either,
instead controlling the rate new clients are activated.
Maybe with some sophisticated profile, single TRex client
can emulate sequence of independent clients (thus controlling
number of open TCP connecton), but I am not sure
the IP selection part is flexible enough in TRex.

The draft probably does not want to allow only some direct inputs,
as different teest equipment vendors have different inputs.
But the draft should require the report with result to specify
which imputs were given.
But I guess that is content suitable for a separate RFC,
discussing test equipment validation.

DUT state
---------

This draft is not targeted at NAT testing.
There are no resetters, there is ramp-up,
so any CPS tests will hit already opened NAT sessions.

Validation criteria
^^^^^^^^^^^^^^^^^^^

It is not clear what to do if criteria are not met.

I guess the draft terms "target throughput" and "initial throughput"
can be translated to CSIT's "max rate" and "min rate".

But sometimes there is "performance goal" and
"the maximum and average achievable throughput within the validation criteria".

That last one sounds like PDR, so "target throughput" and "performance goal"
can be what manufacturer promises (hopefully just a safety margin below PDR).

Also I think there are three different kinds of results (for a trial measurement).

1. Unstable result is when some telemetry suggests we are outside
the test equipment area of reliability. E.g. duration stretching.
Search should avoid those loads, but it is not clear SUT is at fault.

2. Bad result. TG telemetry is stable, but there is too many transaction failures
or other stuff hinting SUT does not work well enough.
PDR searches for boundary of this.

3. Good result. TG is stable and SUT forwards within allowed tolerances.

Types 1 and 2 may be hard to distinguish, especially when TCP is in play.
That is why it is a good idea for PDR search to treat them as the same,
but use different DUT settings to decide which compunents is the bottleneck
(as we do for NAT44ED vs IP4base).
Either way, not sure how "validation criteria" fit with this classification.

Throughput
^^^^^^^^^^

It seems the same word "throughput" is used to mean different quantities depending on context.
Close examination suggests it probably means forwarding rate (see below)
except the offered load is not given explicitly (and maybe is not even constant).

Existing RFCs
-------------

RFC 2544
________

Throughput: https://tools.ietf.org/html/rfc2544#section-26.1

RFC 2285
________

Intended load: https://tools.ietf.org/html/rfc2285#section-3.5.1
Offered load: https://tools.ietf.org/html/rfc2285#section-3.5.2
Maximum offered load: https://tools.ietf.org/html/rfc2285#section-3.5.3
Forwarding rate: https://tools.ietf.org/html/rfc2285#section-3.6.1
FRMOL: https://tools.ietf.org/html/rfc2285#section-3.6.2
FMR: https://tools.ietf.org/html/rfc2285#section-3.6.3

RFC 2889
________

Throughput (updated): https://tools.ietf.org/html/rfc2889#section-5.1.4.1
Forwarding rate (updated): https://tools.ietf.org/html/rfc2889#section-5.1.4.2

Ideas for other drafts
^^^^^^^^^^^^^^^^^^^^^^

DUT traffic-induced state, size-limited trials, state reset (xor ramp-up),
computed trial duration.
List all differences from continuous (DUT as if stateless) trials.