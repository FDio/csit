# Copyright (c) 2019 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for numerical integration, tightly coupled to PLRsearch algorithm.

See log_plus for an explanation why None acts as a special case "float" number.

TODO: Separate optimizations specific to PLRsearch and distribute the rest
      as a standalone package so other projects may reuse.
"""

import copy
import math
import traceback

import dill
import numpy

# TODO: The preferred way to consume this code is via a pip package.
# If your project copies code instead, make sure your pylint check does not
# require these imports to be absolute and descending from your superpackage.
from log_plus import log_plus
import stat_trackers


def try_estimate_nd(communication_pipe, scale_coeff=8.0, trace_enabled=False):
    """Call estimate_nd but catch any exception and send traceback."""
    try:
        return estimate_nd(communication_pipe, scale_coeff, trace_enabled)
    except BaseException:
        # Any subclass could have caused estimate_nd to stop before sending,
        # so we have to catch them all.
        traceback_string = traceback.format_exc()
        communication_pipe.send(traceback_string)
        # After sendig, re-raise, so usages other than "one process per call"
        # keep behaving correctly.
        raise


# FIXME: Pylint reports multiple complexity violations.
# Refactor the code, using less (but structured) variables
# and function calls for (relatively) loosly coupled code blocks.
def estimate_nd(communication_pipe, scale_coeff=8.0, trace_enabled=False):
    """Use Bayesian inference from control queue, put result to result queue.

    TODO: Use a logging framework that works in a user friendly way.
    (Note that multiprocessing_logging does not work well with robot
    and robotbackgroundlogger only works for threads, not processes.
    Or, wait for https://github.com/robotframework/robotframework/pull/2182
    Anyway, the current implementation with trace_enabled looks ugly.)

    The result is average and standard deviation for posterior distribution
    of a single dependent (positive scalar) value.
    The prior is assumed to be uniform on (-1, 1) for every parameter.
    Number of parameters and the function for computing
    the dependent value and likelihood both come from input.

    The likelihood is assumed to be extremely uneven (but never zero),
    so the function should return the logarithm of the likelihood.
    The integration method is basically a Monte Carlo
    (TODO: Add links to notions used here.),
    but importance sampling is used in order to focus
    on the part of parameter space with (relatively) non-negligible likelihood.

    Multivariate Gauss distribution is used for focusing,
    so only unimodal posterior distributions are handled correctly.
    Initial samples are mostly used for shaping (and shifting)
    the Gaussian distribution, later samples will probably dominate.
    Thus, initially the algorithm behavior resembles more "find the maximum",
    as opposed to "reliably integrate". As for later iterations of PLRsearch,
    it is assumed that the distribution position does not change rapidly;
    thus integration algorithm returns also the distribution data,
    to be used as initial focus in next iteration.

    After some number of samples (depends on dimension),
    the algorithm starts tracking few most likely samples to base the Gaussian
    distribution around, mixing with estimates from observed samples.
    The idea is that even when (usually) one of the samples dominates,
    first few are treated as if equally likely, to get reasonable focus.
    During the "find the maximum" phase, this set of best samples
    frequently takes a wrong shape (compared to observed samples
    in equilibrium). Therefore scale_coeff argument is left for humans to tweak,
    so the convergence is reliable and quick.
    Any data (other than correctly weighted samples) used to keep
    distribution shape reasonable is called "bias", regardles of
    whether it comes from input focus, or from tracking top samples.

    Until the distribution locates itself roughly around
    the maximum likeligood point, the integration results are probably wrong.
    That means some minimal time is needed for the result to become reliable.
    The reported standard distribution attempts to signal inconsistence
    (when one sample has dominating weight compared to the rest of samples),
    but some human supervision is strongly encouraged.

    To facilitate running in worker processes, arguments and results
    are communicated via pipe. The computation does not start
    until arguments appear in the pipe, the computation stops
    when another item (stop object) is detected in the pipe
    (and result is put to pipe).

    TODO: Create classes for arguments and results,
          so their fields are documented (and code perhaps more readable).

    Input/argument object (received from pipe)
    is a 4-tuple of the following fields:
    - dimension: Integer, number of parameters to consider.
    - dilled_function: Function (serialized using dill), which:
    - - Takes the dimension number of float parameters from (-1, 1).
    - - Returns float 2-tuple of dependent value and parameter log-likelihood.
    - param_focus_tracker: VectorStatTracker to use for initial focus.
    - max_samples: None or a limit for samples to use.

    Output/result object (sent to pipe queue)
    is a 5-tuple of the following fields:
    - value_tracker: ScalarDualStatTracker estimate of value posterior.
    - param_focus_tracker: VectorStatTracker to use for initial focus next.
    - debug_list: List of debug strings to log at main process.
    - trace_list: List of trace strings to pass to main process if enabled.
    - samples: Number of samples used in computation (to make it reproducible).
    Trace strings are very verbose, it is not recommended to enable them.
    In they are not enabled, trace_list will be empty.
    It is recommended to edit some lines manually to debug_list if needed.

    :param communication_pipe: Pipe to comunicate with boss process.
    :param scale_coeff: Float number to tweak convergence speed with.
    :param trace_enabled: Whether trace list should be populated at all.
        Default: False
    :type communication_pipe: multiprocessing.Connection (or compatible)
    :type scale_coeff: float
    :type trace_enabled: boolean
    :raises OverflowError: If one sample dominates the rest too much.
        Or if value_logweight_function does not handle
        some part of parameter space carefully enough.
    :raises numpy.linalg.LinAlgError: If the focus shape gets singular
        (due to rounding errors). Try changing scale_coeff.
    """

    debug_list = list()
    trace_list = list()
    # Block until input object appears.
    dimension, dilled_function, param_focus_tracker, max_samples = (
        communication_pipe.recv())
    debug_list.append("Called with param_focus_tracker {tracker!r}"
                      .format(tracker=param_focus_tracker))
    def trace(name, value):
        """
        Add a variable (name and value) to trace list (if enabled).

        This is a closure (not a pure function),
        as it accesses trace_list and trace_enabled
        (without any of them being an explicit argument).

        :param name: Any string identifying the value.
        :param value: Any object to log repr of.
        :type name: str
        :type value: object
        """
        if trace_enabled:
            trace_list.append(name + " " + repr(value))
    value_logweight_function = dill.loads(dilled_function)
    samples = 0
    # Importance sampling produces samples of higher weight (important)
    # more frequently, and corrects that by adding weight bonus
    # for the less frequently (unimportant) samples.
    # But "corrected_weight" is too close to "weight" to be readable,
    # so "importance" is used instead, even if it runs contrary to what
    # important region is.
    value_tracker = stat_trackers.ScalarDualStatTracker()
    param_sampled_tracker = stat_trackers.VectorStatTracker(dimension).reset()
    if not param_focus_tracker:
        # First call has None instead of a real (even empty) tracker.
        param_focus_tracker = stat_trackers.VectorStatTracker(dimension)
        param_focus_tracker.unit_reset()
    else:
        # Focus tracker has probably too high weight.
        param_focus_tracker.log_sum_weight = None
    numpy.random.seed(0)
    while not communication_pipe.poll():
        if max_samples and samples >= max_samples:
            break
        # Generate next sample.
        averages = param_focus_tracker.averages
        covariance_matrix = copy.deepcopy(param_focus_tracker.covariance_matrix)
        for first in range(dimension):
            for second in range(dimension):
                covariance_matrix[first][second] *= scale_coeff
        while 1:
            # TODO: Inform pylint that correct version of numpy is available.
            sample_point = numpy.random.multivariate_normal(
                averages, covariance_matrix, 1)[0].tolist()
            # Multivariate Gauss can fall outside (-1, 1) interval
            for first in range(dimension):
                sample_coordinate = sample_point[first]
                if sample_coordinate <= -1.0 or sample_coordinate >= 1.0:
                    break
            else:  # These two breaks implement "level two continue".
                break
        trace("sample_point", sample_point)
        samples += 1
        trace("samples", samples)
        value, log_weight = value_logweight_function(trace, *sample_point)
        trace("value", value)
        trace("log_weight", log_weight)
        trace("focus tracker before adding", param_focus_tracker)
        # Update focus related statistics.
        param_distance = param_focus_tracker.add_without_dominance_get_distance(
            sample_point, log_weight)
        # The code above looked at weight (not importance).
        # The code below looks at importance (not weight).
        log_rarity = param_distance / 2.0
        trace("log_rarity", log_rarity)
        log_importance = log_weight + log_rarity
        trace("log_importance", log_importance)
        value_tracker.add(value, log_importance)
        # Update sampled statistics.
        param_sampled_tracker.add_get_shift(sample_point, log_importance)
    debug_list.append("integrator used " + str(samples) + " samples")
    debug_list.append(
        "value_avg " + str(value_tracker.average)
        + " param_sampled_avg " + repr(param_sampled_tracker.averages)
        + " param_sampled_cov " + repr(param_sampled_tracker.covariance_matrix)
        + " value_log_variance " + str(value_tracker.log_variance)
        + " value_log_secondary_variance " + str(value_tracker.secondary.log_variance))
    communication_pipe.send(
        (value_tracker, param_focus_tracker, debug_list, trace_list, samples))
