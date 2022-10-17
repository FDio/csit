.. _packet_flow_ordering:

Packet Flow Ordering
^^^^^^^^^^^^^^^^^^^^

TRex Traffic Generator (TG) supports two main ways how to cover
address space (on allowed ranges) in scale tests.

In most cases only one field value (e.g. IPv4 destination address) is
altered, in some cases two fields (e.g. IPv4 destination address and UDP
destination port) are altered.

Incremental Ordering
~~~~~~~~~~~~~~~~~~~~

This case is simpler to implement and offers greater control.

When changing two fields, they can be incremented synchronously, or one
after another. In the latter case we can specify which one is
incremented each iteration and which is incremented by "carrying over"
only when the other "wraps around". This way also visits all
combinations once before the "carry" field also wraps around.

It is possible to use increments other than 1.

Randomized Ordering
~~~~~~~~~~~~~~~~~~~

This case chooses each field value at random (from the allowed range).
In case of two fields, they are treated independently.
TRex allows to set random seed to get deterministic numbers.
We use a different seed for each field and traffic direction.
The seed has to be a non-zero number, we use 1, 2, 3, and so on.

The seeded random mode in TRex requires a "limit" value,
which acts as a cycle length limit (after this many iterations,
the seed resets to its initial value).
We use the maximal allowed limit value (computed as 2^24 - 1).

Randomized profiles do not avoid duplicated values,
and do not guarantee each possible value is visited,
so it is not very useful for stateful tests.
