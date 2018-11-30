# Copyright (c) 2018 Cisco and/or its affiliates.
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

TODO: Separate optimizations specific to PLRsearch
      and distribute as a standalone package so other projects may reuse.
"""

import math
import random
import time
import traceback

import dill
import numpy

from log_plus import log_plus


# Two numerical constants to save some cycles.
Integrator__HALF_PI = math.acos(0)
Integrator__DOUBLE_PI = 4 * Integrator__HALF_PI


def try_estimate_nd(communication_pipe, scale_coeff=10.0, trace_enabled=False):
    """Call estimate_nd but catch any exception and send traceback."""
    try:
        return estimate_nd(communication_pipe, scale_coeff, trace_enabled)
    except:
        traceback_string = traceback.format_exc()
        communication_pipe.send(traceback_string)


def estimate_nd(communication_pipe, scale_coeff=10.0, trace_enabled=False):
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
    whether it comes from input hint, or from tracking top samples.

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
    - param_hint_avg: Dimension-tuple of floats to start searching around.
    - param_hint_cov: Covariance matrix defining initial focus shape.

    Output/result object (sent to pipe queue)
    is a 6-tuple of the following fields:
    - value_avg: Float estimate of posterior average dependent value.
    - value_stdev: Float estimate of posterior standard deviation of the value.
    - param_importance_avg: Float tuple, center of Gaussian to use next.
    - param_importance_cov: Float covariance matrix of the Gaussian to use next.
    - debug_list: List of debug strings to log at main process.
    - trace_list: List of trace strings to pass to main process if enabled.
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

    # Block until input object appears.
    dimension, dilled_function, param_hint_avg, param_hint_cov = (
        communication_pipe.recv())
    debug_list = list()
    trace_list = list()
    def add_trace(name, value):
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
    len_top = (dimension + 2) * (dimension + 1) / 2
    top_weight_param = list()
    samples = 0
    log_sum_weight = None
    # Importance sampling produces samples of higher weight (important)
    # more frequently, and corrects that by adding weight bonus
    # for the less frequently (unimportant) samples.
    # But "corrected_weight" is too close to "weight" to be readable,
    # so "importance" is used instead, even if it runs contrary to what
    # important region is.
    log_sum_importance = None
    log_importance_best = None
    value_avg = 0.0
    # 1x1 dimensional covariance matrix is just variance.
    # As variance is never negative, we can track logarithm.
    value_log_variance = None
    # Here "secondary" means "excluding the weightest sample".
    log_secondary_sum_importance = None
    value_secondary_avg = 0.0
    value_log_secondary_variance = None
    param_sampled_avg = [0.0 for first in range(dimension)]
    # TODO: Examine whether we can gain speed by tracking triangle only.
    # Covariance matrix can contain negative element (off-diagonal),
    # so no logarithm here. This can lead to zeroes on diagonal,
    # but we have biasing to make sure it does not hurt much.
    param_sampled_cov = [[0.0 for first in range(dimension)]
                         for second in range(dimension)]
    if not (param_hint_avg and param_hint_cov):
        # First call has Nones instead of useful hints.
        param_hint_avg = [0.0 for first in range(dimension)]
        param_hint_cov = [
            [1.0 if first == second else 0.0 for first in range(dimension)]
            for second in range(dimension)]
    while not communication_pipe.poll():
        # Compute focus data.
        if len(top_weight_param) < len_top:
            # Not enough samples for reasonable top, use hint bias.
            param_focus_avg = param_hint_avg
            param_focus_cov = param_hint_cov
        else:
            # We have both top samples and overall samples.
            # Mix them according to how much the weightest sample dominates.
            log_top_weight = top_weight_param[0][0]
            log_weight_norm = log_plus(log_sum_weight, log_top_weight)
            top_ratio = math.exp(log_top_weight - log_weight_norm)
            sampled_ratio = math.exp(log_sum_weight - log_weight_norm)
            add_trace("log_top_weight", log_top_weight)
            add_trace("log_sum_weight", log_sum_weight)
            add_trace("top_ratio", top_ratio)
            add_trace("sampled_ratio", sampled_ratio)
            param_focus_avg = [
                sampled_ratio * param_sampled_avg[first]
                + top_ratio * param_top_avg[first]
                for first in range(dimension)]
            param_focus_cov = [[
                scale_coeff * (
                    sampled_ratio * param_sampled_cov[first][second]
                    + top_ratio * param_top_cov[first][second])
                for first in range(dimension)] for second in range(dimension)]
        add_trace("param_focus_avg", param_focus_avg)
        add_trace("param_focus_cov", param_focus_cov)
        # Generate next sample.
        while 1:
            # Multivariate Gauss can fall outside (-1, 1) interval
            sample_point = numpy.random.multivariate_normal(
                param_focus_avg, param_focus_cov, 1)[0]
            for first in range(dimension):
                sample_coordinate = sample_point[first]
                if sample_coordinate <= -1.0 or sample_coordinate >= 1.0:
                    break
            else:  # These two breaks implement "level two continue".
                break
        add_trace("sample_point", sample_point)
        samples += 1
        value, log_weight = value_logweight_function(*sample_point)
        add_trace("value", value)
        add_trace("log_weight", log_weight)
        # Update bias related statistics.
        log_sum_weight = log_plus(log_sum_weight, log_weight)
        if len(top_weight_param) < len_top:
            top_weight_param.append((log_weight, sample_point))
        if (len(top_weight_param) >= len_top
            # Hack: top_weight_param[-1] is either the smallest,
            #       or the just appended to len_top-1 item list.
            and log_weight >= top_weight_param[-1][0]):
            # The line above is still part if the if expression.
            top_weight_param = top_weight_param[:-1]
            top_weight_param.append((log_weight, sample_point))
            top_weight_param.sort(key=lambda item: -item[0])
            add_trace("top_weight_param", top_weight_param)
            # top_weight_param has changed, recompute biases.
            param_top_avg = top_weight_param[0][1]
            param_top_cov = [[0.0 for first in range(dimension)]
                              for second in range(dimension)]
            top_item_count = 1
            for _, near_top_param in top_weight_param[1:]:
                top_item_count += 1
                next_item_ratio = 1.0 / top_item_count
                previous_items_ratio = 1.0 - next_item_ratio
                param_shift = [
                    near_top_param[first] - param_top_avg[first]
                    for first in range(dimension)]
                # Do not move center from the weightest sample.
                for second in range(dimension):
                    for first in range(dimension):
                        param_top_cov[first][second] += (
                            param_shift[first] * param_shift[second]
                            * next_item_ratio)
                        param_top_cov[first][second] *= previous_items_ratio
            add_trace("param_top_avg", param_top_avg)
            add_trace("param_top_cov", param_top_cov)
        # The code above looked at weight (not importance).
        # The code below looks at importance (not weight).
        param_shift = [sample_point[first] - param_focus_avg[first]
                       for first in range(dimension)]
        rarity_gradient = numpy.linalg.solve(param_focus_cov, param_shift)
        rarity_step = numpy.vdot(param_shift, rarity_gradient)
        log_rarity = rarity_step / 2.0
        add_trace("log_rarity", log_rarity)
        add_trace("samples", samples)
        log_importance = log_weight + log_rarity
        add_trace("log_importance", log_importance)
        # Update sampled statistics.
        old_log_sum_importance = log_sum_importance
        log_sum_importance = log_plus(old_log_sum_importance, log_importance)
        add_trace("new log_sum_weight", log_sum_weight)
        add_trace("log_sum_importance", log_sum_importance)
        if old_log_sum_importance is None:
            param_sampled_avg = list(sample_point)
            value_avg = value
            # Other value related quantities stay None.
            continue
        previous_samples_ratio = math.exp(
            old_log_sum_importance - log_sum_importance)
        new_sample_ratio = math.exp(log_importance - log_sum_importance)
        param_shift = [sample_point[first] - param_sampled_avg[first]
                       for first in range(dimension)]
        value_shift = value - value_avg
        for first in range(dimension):
            param_sampled_avg[first] += param_shift[first] * new_sample_ratio
        old_value_avg = value_avg
        value_avg += value_shift * new_sample_ratio
        value_absolute_shift = abs(value_shift)
        for second in range(dimension):
            for first in range(dimension):
                param_sampled_cov[first][second] += (
                    param_shift[first] * param_shift[second] * new_sample_ratio)
                param_sampled_cov[first][second] *= previous_samples_ratio
        add_trace("param_sampled_avg", param_sampled_avg)
        add_trace("param_sampled_cov", param_sampled_cov)
        update_secondary_stats = True
        if log_importance_best is None or log_importance > log_importance_best:
            log_importance_best = log_importance
            log_secondary_sum_importance = old_log_sum_importance
            value_secondary_avg = old_value_avg
            value_log_secondary_variance = value_log_variance
            update_secondary_stats = False
            # TODO: Update all primary quantities before secondary ones.
            # (As opposed to current hybrid code.)
        if value_absolute_shift > 0.0:
            value_log_variance = log_plus(
                value_log_variance, 2 * math.log(value_absolute_shift)
                + log_importance - log_sum_importance)
        if value_log_variance is not None:
            value_log_variance -= log_sum_importance - old_log_sum_importance
        if not update_secondary_stats:
            continue
        old_log_secondary_sum_importance = log_secondary_sum_importance
        log_secondary_sum_importance = log_plus(
            old_log_secondary_sum_importance, log_importance)
        if old_log_secondary_sum_importance is None:
            value_secondary_avg = value
            continue
        previous_samples_secondary_ratio = math.exp(
            old_log_secondary_sum_importance - log_secondary_sum_importance)
        new_sample_secondary_ratio = math.exp(
            log_importance - log_secondary_sum_importance)
        old_value_secondary_avg = value_secondary_avg
        value_secondary_shift = value - value_secondary_avg
        value_secondary_absolute_shift = abs(value_secondary_shift)
        value_secondary_avg += (
            value_secondary_shift * new_sample_secondary_ratio)
        if value_secondary_absolute_shift > 0.0:
            value_log_secondary_variance = log_plus(
                value_log_secondary_variance, (
                    2 * math.log(value_secondary_absolute_shift)
                    + log_importance - log_secondary_sum_importance))
        if value_log_secondary_variance is not None:
            value_log_secondary_variance -= (
                log_secondary_sum_importance - old_log_secondary_sum_importance)
    debug_list.append("integrator used " + str(samples) + " samples")
    debug_list.append(
        "value_avg " + str(value_avg)
        + " param_sampled_avg " + repr(param_sampled_avg)
        + " param_sampled_cov " + repr(param_sampled_cov)
        + " value_log_variance " + str(value_log_variance)
        + " value_log_secondary_variance " + str(value_log_secondary_variance))
    value_stdev = math.exp(
        (2 * value_log_variance - value_log_secondary_variance) / 2.0)
    debug_list.append("top_weight_param[0] " + repr(top_weight_param[0]))
    # Intentionally returning param_focus_avg and param_focus_cov,
    # instead of possibly hyper-focused bias or sampled.
    communication_pipe.send(
        (value_avg, value_stdev, param_focus_avg, param_focus_cov, debug_list,
         trace_list))
