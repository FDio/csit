Extended soak test
^^^^^^^^^^^^^^^^^^

This is a draft of design document for new type of test.

Motivation
----------

Network providers are interested in throughput a device can sustain.

RFC 2544 assumes loss ratio is given by a quite deterministic
function of offered load. But software devices are not deterministic enough.
This leads deterministic algorithms (such as MLRsearch with single trial)
to return results with relatively high standard deviation,
thus making it harder to tell what "the throughput" is.

We need another algorithm, which takes the indeterminism into account.

Model
-----

Each algorithm searches for an answer to a precisely formulated question.
When the question involves indeterministi systems, it has to specify
probabilities (or prior distributions) which are tied
to a specific probabilistic model. Different models will have different number
(and meaning) of parameters. Complicated (but more realistic) models
have many parameters, and the math involved can be very complicated.
It is better to start with simpler probabilistic model,
and only change it when output of the algorithm is not stable
or useful enough.

This document is focused on algorithms related to packet loss count only
(no latency information is taken into account)
and (for simplicity) only one type of trials is considered:
repeated one-second trial.

In current CSIT code, there is around 0.5 second delay between trials,
avoiding that is out of scope of this document.

Also, running longer trials (in some situations) could be more efficient,
but BMRR tests show that the effect of trial duration on loss count
can be non-linear, so this document sticks to 1s trials only.

Poisson distribution
--------------------

Wiki link: https://en.wikipedia.org/wiki/Poisson_distribution

For given offered load, number of packets lost during 1s trial
is assumed to come from Poisson distribution,
each trial is assumed to be independent, and the (unknown) parameter
(average number of packets lost per second) is constant across trials.

When comparing different loads, the average is assumed to increase,
but the (deterministic) function from offered load into average loss
is otherwise unknown.

Given a loss target (say one packet lost per second),
there is an unknown offered load when the average is exactly that.
We call that the critical load.

Of course, there are great many increasing functions.
The offered load has to be chosen for each trial,
and the computed distribution of critical load
can change with each trial result.

To make the space of possible functions more tractable,
some other simplifying assumption is needed.
As the algorithm will be examining (also) loads close to the critical load,
we can assume the function will be roughly linear in small vicinity
of the critical load. Results from trials far from the critical load estimate
have to be discarded, as they will very probably be far from linear.

This still leaves two quite natural approaches to the search.
One uses binary search (probably MLRsearch) to track upper and lower bounds,
and only results from recent bound loads are to be examined.
Othe approach is to change the offered load after each trial,
and discard earlier results based on current average and stdev.

This document focuses on the latter, "dynamic" approach.

Linear coefficient distribution
-------------------------------

Packet loss cannot be negative, so by "linear" function
we meen a function which starts as zero, and switches to linear increase
at some load. Packet loss count also cannot be higher than
number of offered packets, so the slope of the linear part is limited.

Put together, we have two parameters and natural uniform distributions
for their values.

First parameter is "safe load", the maximum load when the loss is zero.
If we name "excess load" the difference between offered load and safe load,
then "excess loss ratio" is the slope constant (between zero and one)
indicating how much the average loss count increases when increasing
the excess load by one packet per second.

Prior distribution for safe load is assumed to be uniform
from zero offered load to maximum load
(given by NIC, PCI, line bandwidth or similar).
Prior distribution for excess loss ratio is assumed to be uniform
from zero to one.
If those priors lead to unreasonably long search,
we could add biases, based on the data seen.

Discard strategy: After computing average and stdev for posterior distribution
of the critical load, results of trials outsize offered load interval
(avg - stdev, avg + stdev) are discarded (and never taken into acount again
when the interval boundaries move, new trials have to be executed;
otherwise the remove/add cycle might never end).

Speaking about new trials, each next trial will be done
at offered load equal to the current average of the critical load.

Exit condition is critical load stdev becoming small enough,
say 0.5% of the current average.

The algorithm should report both avg and stdev, both for critical load
and for safe load (as no doubd users will be interested in that).

Math
----

Start by tracking first few posteriors, see if a closed form emerges.

(I got a feeling the posterior distributions will not be integrable.)
