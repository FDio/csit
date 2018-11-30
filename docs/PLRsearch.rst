PLRsearch
^^^^^^^^^

TODO: Make this not an orphan document.

This is a draft of design document for new type of test.

Motivation
~~~~~~~~~~

Network providers are interested in throughput a device can sustain.

RFC 2544 assumes loss ratio is given by a quite deterministic
function of offered load. But software devices are not deterministic enough.
This leads deterministic algorithms (such as MLRsearch with single trial)
to return results, which when repeated show relatively high standard deviation,
thus making it harder to tell what "the throughput" is.

We need another algorithm, which takes the indeterminism into account.

Model
~~~~~

Each algorithm searches for an answer to a precisely formulated question.
When the question involves indeterministic systems, it has to specify
probabilities (or prior distributions) which are tied
to a specific probabilistic model. Different models will have different number
(and meaning) of parameters. Complicated (but more realistic) models
have many parameters, and the math involved can be very complicated.
It is better to start with simpler probabilistic model,
and only change it when the output of the simpler algorithm is not stable
or useful enough.

This document is focused on algorithms related to packet loss count only
(no latency information is taken into account)
and (for simplicity) only one type of trials is considered:
repeated trials of constant trial duration (customizable, 1 second by default).

In current CSIT code, there is around 0.5 second delay between trials,
avoiding that is out of scope of this document.

Also, running longer trials (in some situations) could be more efficient,
but BMRR tests show that the effect of trial duration on loss count
can be non-linear, so this document sticks to 1s (or otherwise constant)
trial durations only.

Poisson distribution
~~~~~~~~~~~~~~~~~~~~

Wiki link: https://en.wikipedia.org/wiki/Poisson_distribution

For given offered load, number of packets lost during trial
is assumed to come from Poisson distribution,
each trial is assumed to be independent, and the (unknown) parameter
(average number of packets lost per second) is constant across trials.

When comparing different loads, the average is assumed to increase,
but the (deterministic) function from offered load into average loss
is otherwise unknown.

Given a loss target (configurable, by default one packet lost per second),
there is an unknown offered load when the average is exactly that.
We call that the "critical load".
If critical load seems higher than maximum offerable load,
we should use the maximum to make avg reasonable and stdev lower.

Of course, there are great many increasing functions.
The offered load has to be chosen for each trial,
and the computed distribution of critical load
can change with each trial result.

To make the space of possible functions more tractable,
some other simplifying assumption is needed.
As the algorithm will be examining (also) loads close to the critical load,
we can assume the function will be roughly linear in small vicinity
of the critical load.
Results from trials far from the critical load estimate
could be discarded (as they will very probably be far from linear),
but discarding when boundary is not exact is never optimal.
Instead, distant trials could be "supressed" when computing
posterior distribution. This means their probabilities will not be used
for multiplying, just some small powers od them.

This document focuses on an approach which change the offered load
after each trial, based on posterior probabilities (with supressing).

Linear coefficient distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Packet loss cannot be negative, so by "linear" function
we mean a function which starts as zero, and switches to linear increase
at some load. Packet loss count also cannot be higher than
number of offered packets, so the slope of the linear part is limited by one.

Put together, we have two parameters and natural uniform distributions
for their values.

First parameter is "safe load", the maximum load when the loss is zero.
If we name "excess load" the difference between offered load and safe load,
then "excess loss ratio" is the slope constant (between zero and one)
indicating how much the average loss count increases when increasing
the excess load by one packet per second.

Prior distribution for safe load is assumed to be uniform
from zero offered load to maximum load limit
(given by NIC, PCI, line bandwidth, or similar).
Prior distribution for excess loss ratio is assumed to be uniform
from zero to one.
If those priors lead to unreasonably long search,
we could add biases, based on the data seen.

Supression strategy: After computing average and stdev
for posterior distribution of the critical load,
probabilities of trial results are supressed harmionically.
Result from average is taken with full probability, result from stdev distance
is taken as square root of the probability, result from two stdevs
as probability to the power of 1/5, n stdevs with power of 1/(1+n*n).

Speaking about new trials, each next trial will be done
at offered load equal to the current average of the critical load.

Exit condition is critical load stdev becoming small enough,
say 0.5% of the current average.

The algorithm should report both avg and stdev, both for critical load
and for safe load (as no doubd users will be interested in that).

Math
~~~~

Start by tracking first few posteriors, see if a closed form emerges.

The function: avg_loss(offered_load; safe_load, excess_loss_ratio) =
= max(0, excess_loss_ratio * (offered_load - safe_load)).

Probability of seeing loss_count at given avg_loss is:
(avg_loss ** loss_count) * exp(-avg_loss) / factorial(loss_count).

critical_load = min(maximal_load, safe_load + 1.0 / excess_loss_ratio)

Integration
-----------

I have a feeling the posterior distributions will not be integrable.

Nevermind, we only have two parameter space,
numeric integration should be reliable enough.

But at the start, simple grid method should work well enough.

Do we need a specific numeric stability condition?

Optimizations
~~~~~~~~~~~~~

Seeing nonzero loss at a load means no safe load
higher than that have nonzero weight.
No amount of supression changes that, which might lead
to artificially low excess ratios and thus large stdev of critical rate.
This might be either good or bad, we will see.

After enough trials, the posterior will be concentrated in narrow area
of safe load, probably also somewhat narrow in excess loss ratio
(with large correlation). The integration method could take advantage of that.
Already tried, integration is entirely unusable without some optimization here.

Generally, the 1.5 second of waiting for the trial result can be used
for running the numerical integration (as opposed to waiting for the integration
to reach a specific acuracy goal).
This means the algorithm would use two threads.

Next steps
~~~~~~~~~~

It might be good idea to code loss simulator with nonlinear function first.
It can use the same API as the simulator for MLRsearch,
just add realistic enough Measurer implementation. DONE.

Then code the algorithm, run it against the simulator. DONE.

Fix the algorithm so that it is at least somewhat reliable with simulator.

Then run it against real system.

Then tweak simulator to become more similar to the real system.

Then start tweaking the algorithm to squeeze some time savings.
