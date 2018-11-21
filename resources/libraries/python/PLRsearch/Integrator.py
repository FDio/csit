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
TODO: Make sure logging works as expected also when called from Robot.
"""

import copy
import logging
import math
import random
import time

import numpy

from log_plus import log_plus


# Two numerical constants to save some cycles.
Integrator__HALF_PI = math.acos(0)
Integrator__DOUBLE_PI = 4 * Integrator__HALF_PI

def estimate_nd(control_queue, result_queue, scale_coeff=10.0):
    """Use Bayesian inference from control queue, put result to result queue.

    TODO: Make sure logging works correctly also when started from Robot.
    TODO: Delete the commented-out debug prints (or change to trace logs).

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
    it is assumed that the distribution position does not change rapidly,
    this integration algorithm returns also the distribution data,
    to be used as initial focus in next iteration.

    After some number of samples (depends on dimension),
    the algorithm starts tracking few most likely samples to base the Gaussian
    distribution around, mixing with estimates from observed samples.
    During the "find the maximum" phase, this set of best samples
    frequently takes a wrong shape (compared to focus in equilibrium),
    scale_coeff argument is left for humans to tweak,
    so the convergence is reliable and quick.

    Thus, until the distribution locates itself roughly around
    the maximum likeligood point, the integration results are probably wrong.
    That means some minimal time is needed for the result to become reliable.
    The reported standard distribution attempts to signal inconsistence
    (when one sample has dominating weight compared to the rest of samples),
    but some human supervision is strongly encouraged.

    To facilitate running in worker threads, arguments and results
    are communicated via queues. The computation does not start
    until arguments appear in the control queue, the computation stops
    when another item (stop object) is detected on the control queue.

    TODO: Create classes for arguments and results,
          so their fields are documented (and code perhaps more readable).

    Input/argument object (taken from control queue)
    is a 4-tuple of the following fields:
    - dimension: Integer, number of parameters to consider.
    - value_logweight_function: Function, which:
    - - Takes the dimension number of float parameters from (-1, 1).
    - - Returns float 2-tuple of dependent value and parameter log-likelihood.
    - param_bias_avg: Dimension-tuple of floats to start searching around.
    - param_bias_cov: Covariance matrix defining initial focus shape.

    Output/result object (pushed to result queue)
    is a 4-tuple of the following fields:
    - value_avg: Float estimate of posterior average dependent value.
    - value_stdev: Float estimate of posterior standard deviation of the value.
    - param_importance_avg: Float tuple, center of Gaussian to use next.
    - param_importance_cov: Float covariance matrix of the Gaussian to use next.

    Note that the two queues are used as unidirectional pipes,
    but they cannot be combined into a single queue.
    In that case, the management thread would have trouble distinguishing
    the stop object from the computation result.

    :param control_queue: Queue to read input and stop objects from.
    :param result_queue: Queue to put result object into.
    :param scale_coeff: Float number to tweak convergence speed with.
    :type control_queue: Any queue, Queue.Queue semantics expected.
    :type result_queue: Any queue, Queue.Queue semantics expected.
    :raises OverflowError: If one sample dominates the rest too much.
        Or if value_logweight_function does not handle
        some part of parameter space carefully enough.
    :raises numpy.linalg.LinAlgError: If the focus shape gets singular
        (due to rounding errors). Try changing scale_coeff.
    """

    dimension, value_logweight_function, param_bias_avg, param_bias_cov = (
        control_queue.get())
    len_top = (dimension + 2) * (dimension + 1) / 2
    top_weight_param = list()
    samples = 0
    log_sum_weight = None
    log_sum_importance = None
    log_importance_best = None
    value_avg = 0.0
    value_log_variance = None
    log_secondary_sum_importance = None
    value_secondary_avg = 0.0
    value_log_secondary_variance = None
    param_sampled_avg = [0.0 for first in range(dimension)]
    # TODO: Examine whether we can gain speed by tracking triangle only.
    param_sampled_cov = [[0.0 for first in range(dimension)]
                         for second in range(dimension)]
    if not (param_bias_avg and param_bias_cov):
        param_bias_avg = [0.0 for first in range(dimension)]
        param_bias_cov = [
            [1.0 if first == second else 0.0 for first in range(dimension)]
            for second in range(dimension)]
    while control_queue.empty():
        # Compute importance data.
        if len(top_weight_param) < len_top:
            param_importance_avg = list(param_bias_avg)
            param_importance_cov = copy.deepcopy(param_bias_cov)
        else:
            param_bias_log_weight = top_weight_param[0][0]
            log_weight_norm = log_plus(log_sum_weight, param_bias_log_weight)
            bias_ratio = math.exp(param_bias_log_weight - log_weight_norm)
            sampled_ratio = math.exp(log_sum_weight - log_weight_norm)
#            print "param_bias_log_weight", param_bias_log_weight,
#            print "log_sum_weight", log_sum_weight, "bias_ratio", bias_ratio,
#            print "sampled_ratio", sampled_ratio
            param_importance_avg = [
                sampled_ratio * param_sampled_avg[first]
                + bias_ratio * param_bias_avg[first]
                for first in range(dimension)]
            param_importance_cov = [[
                scale_coeff * (
                    sampled_ratio * param_sampled_cov[first][second]
                    + bias_ratio * param_bias_cov[first][second])
                for first in range(dimension)] for second in range(dimension)]
#        print "param_importance_avg", repr(param_importance_avg),
#        print "param_importance_cov", repr(param_importance_cov)
        while 1:
            sample_point = numpy.random.multivariate_normal(
                param_importance_avg, param_importance_cov, 1)[0]
            for first in range(dimension):
                sample_coordinate = sample_point[first]
                if sample_coordinate <= -1.0 or sample_coordinate >= 1.0:
                    break
            else:  # These two breaks implement "level two continue".
                break
#        print "DEBUG sample_point", repr(sample_point)
        samples += 1
        value, log_weight = value_logweight_function(*sample_point)
#        print "value", value, "log_weight", log_weight
        log_sum_weight = log_plus(log_sum_weight, log_weight)
        if len(top_weight_param) < len_top:
            top_weight_param.append((log_weight, sample_point))
        # Hack: top_weight_param[-1] is either smallest,
        #       or just appended to len_top-1 item list.
        if (len(top_weight_param) >= len_top
            and log_weight >= top_weight_param[-1][0]):
            top_weight_param = top_weight_param[:-1]
            top_weight_param.append((log_weight, sample_point))
            top_weight_param.sort(key=lambda item: -item[0])
#            print "DEBUG top_weight_param", repr(top_weight_param)
            # top_weight_param has changed, recompute biases
            param_bias_avg = top_weight_param[0][1]
            param_bias_cov = [[0.0 for first in range(dimension)]
                              for second in range(dimension)]
            top_item_count = 1
            for _, near_top_param in top_weight_param[1:]:
                top_item_count += 1
                next_item_ratio = 1.0 / top_item_count
                previous_items_ratio = 1.0 - next_item_ratio
                param_shift = [
                    near_top_param[first] - param_bias_avg[first]
                    for first in range(dimension)]
                # Do not move center from biggest point
                for second in range(dimension):
                    for first in range(dimension):
                        param_bias_cov[first][second] += (
                            param_shift[first] * param_shift[second]
                            * next_item_ratio)
                        param_bias_cov[first][second] *= previous_items_ratio
#            print "param_bias_avg", repr(param_bias_avg),
#            print "param_bias_cov", repr(param_bias_cov)
        param_shift = [sample_point[first] - param_importance_avg[first]
                       for first in range(dimension)]
        rarity_gradient = numpy.linalg.solve(param_importance_cov, param_shift)
        rarity_step = numpy.vdot(param_shift, rarity_gradient)
        log_rarity = rarity_step / 2.0
#        print "log_rarity", log_rarity, "samples", samples
        log_importance = log_weight + log_rarity
#        print "log_importance", log_importance
        old_log_sum_importance = log_sum_importance
        log_sum_importance = log_plus(old_log_sum_importance, log_importance)
#        print "new log_sum_weight", log_sum_weight,
#        print "log_sum_importance", log_sum_importance
        if old_log_sum_importance is None:
            param_sampled_avg = list(sample_point)
            value_avg = value
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
#        print "param_sampled_avg", repr(param_sampled_avg),
#        print "param_sampled_cov", repr(param_sampled_cov)
        update_secondary_stats = True
        if log_importance_best is None or log_importance > log_importance_best:
            log_importance_best = log_importance
            log_secondary_sum_importance = old_log_sum_importance
            value_secondary_avg = old_value_avg
            value_log_secondary_variance = value_log_variance
            update_secondary_stats = False
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
    logging.debug("integrator used " + str(samples) + " samples")
    logging.debug(
        "value_avg " + str(value_avg)
        + " param_sampled_avg " + repr(param_sampled_avg)
        + " param_sampled_cov " + repr(param_sampled_cov)
        + " value_log_variance " + str(value_log_variance)
        + " value_log_secondary_variance " + str(value_log_secondary_variance))
    value_stdev = math.exp(
        (2 * value_log_variance - value_log_secondary_variance) / 2.0)
    logging.debug("top_weight_param[0] " + repr(top_weight_param[0]))
    # Intentionally returning param_importance_avg, param_importance_cov
    # instead of hyper-focused bias.
    result_queue.put(
        (value_avg, value_stdev, param_importance_avg, param_importance_cov))
