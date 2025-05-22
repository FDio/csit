Multiple Loss Ratio Search library
==================================

Origins
-------

This library was developed as a speedup for traditional binary search
in CSIT_ (Continuous System and Integration Testing) project of fd.io_
(Fast Data), one of LFN_ (Linux Foundation Networking) projects.

In order to make this code available in PyPI_ (Python Package Index),
the setuputils stuff (later converted to pyproject.toml) has been added,
but after some discussion, that directory_ ended up having
only a symlink to the original place of tightly coupled CSIT code.

IETF documents
--------------

The currently published `IETF draft`_ describes the logic of version 1.2.0,
earlier library and draft versions do not match each other that well.

Usage
-----

High level description
______________________

A complete application capable of testing performance using MLRsearch
consists of three layers: Manager, Controller and Measurer.
This library provides an implementation for the Controller only,
including all the classes needed to define API between Controller
and other two components.

Users are supposed to implement the whole Manager layer,
and also implement the Measurer layer.
The Measurer instance is injected as a parameter
when the manager calls the controller instance.

The purpose of Measurer instance is to perform one trial measurement.
Upon invocation of measure() method, the controller only specifies
the intended duration and the intended load for the trial.
The call is done using keyword arguments, so the signature has to be:

..  code-block:: python3

    def measure(self, intended_duration, intended_load):

Usually, the trial measurement process also needs other values,
collectively caller a traffic profile. User (the manager instance)
is responsible for initiating the measurer instance accordingly.
Also, the manager is supposed to set up SUT, traffic generator,
and any other component that can affect the result.

For specific input and output objects see the example below.

Example
_______

This is a minimal example showing every configuration attribute.
The measurer does not interact with any real SUT,
it simulates a SUT that is able to forward exactly one million packets
per second (unidirectional traffic only),
not one packet more (fully deterministic).
In these conditions, the conditional throughput for PDR
happens to be accurate within one packet per second.

This is the screen capture of interactive python interpreter
(wrapped so long lines are readable):

..  code-block:: python3

    >>> import dataclasses
    >>> from MLRsearch import (
    ...     AbstractMeasurer, Config, MeasurementResult,
    ...     MultipleLossRatioSearch, SearchGoal,
    ... )
    >>>
    >>> class Hard1MppsMeasurer(AbstractMeasurer):
    ...     def measure(self, intended_duration, intended_load):
    ...         sent = int(intended_duration * intended_load)
    ...         received = min(sent, int(intended_duration * 1e6))
    ...         return MeasurementResult(
    ...             intended_duration=intended_duration,
    ...             intended_load=intended_load,
    ...             offered_count=sent,
    ...             forwarded_count=received,
    ...         )
    ...
    >>> def print_dot(_):
    ...     print(".", end="")
    ...
    >>> ndr_goal = SearchGoal(
    ...     loss_ratio=0.0,
    ...     exceed_ratio=0.005,
    ...     relative_width=0.005,
    ...     initial_trial_duration=1.0,
    ...     final_trial_duration=1.0,
    ...     duration_sum=21.0,
    ...     preceding_targets=2,
    ...     expansion_coefficient=2,
    ... )
    >>> pdr_goal = dataclasses.replace(ndr_goal, loss_ratio=0.005)
    >>> config = Config(
    ...     goals=[ndr_goal, pdr_goal],
    ...     min_load=1e3,
    ...     max_load=1e9,
    ...     search_duration_max=1.0,
    ...     warmup_duration=None,
    ... )
    >>> controller = MultipleLossRatioSearch(config=config)
    >>> result = controller.search(measurer=Hard1MppsMeasurer(), debug=print_dot)
    ....................................................................................
    ....................................................................................
    ...................>>> print(result)
    {SearchGoal(loss_ratio=0.0, exceed_ratio=0.005, relative_width=0.005, initial_trial_
    duration=1.0, final_trial_duration=1.0, duration_sum=21.0, preceding_targets=2, expa
    nsion_coefficient=2, fail_fast=True): fl=997497.6029392382,s=(gl=21.0,bl=0.0,gs=0.0,
    bs=0.0), SearchGoal(loss_ratio=0.005, exceed_ratio=0.005, relative_width=0.005, init
    ial_trial_duration=1.0, final_trial_duration=1.0, duration_sum=21.0, preceding_targe
    ts=2, expansion_coefficient=2, fail_fast=True): fl=1002508.6747611101,s=(gl=21.0,bl=
    0.0,gs=0.0,bs=0.0)}
    >>> print(f"NDR conditional throughput: {float(result[ndr_goal].conditional_throughp
    ut)}")
    NDR conditional throughput: 997497.6029392382
    >>> print(f"PDR conditional throughput: {float(result[pdr_goal].conditional_throughp
    ut)}")
    PDR conditional throughput: 1000000.6730730429
    >>>

Change log
----------

1.2.1: Updated the readme document.

1.2.0: Changed the output structure to use Goal Result as described in draft-05.

1.1.0: Logic improvements, independent selectors, exceed ratio support,
better width rounding, conditional throughput as output.
Implementation relies more on dataclasses, code split into smaller files.
API changed considerably, mainly to avoid long argument lists.

0.4.0: Considarable logic improvements, more than two target ratios supported.
API is not backward compatible with previous versions.

0.3.0: Migrated to Python 3.6, small code quality improvements.

0.2.0: Optional parameter "doublings" has been added.

0.1.1: First officially released version.

.. _CSIT: https://wiki.fd.io/view/CSIT
.. _fd.io: https://fd.io/
.. _LFN: https://www.linuxfoundation.org/projects/networking/
.. _PyPI: https://pypi.org/project/MLRsearch/
.. _directory: https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch
.. _IETF draft: https://tools.ietf.org/html/draft-ietf-bmwg-mlrsearch-05
