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

"""Module holding PLRsearch class."""

import logging
import math
import multiprocessing
import time

import dill
# TODO: Inform pylint about scipy (of correct version) being available.
from scipy.special import erfcx, erfc

# TODO: The preferred way to consume this code is via a pip package.
# If your project copies code instead, make sure your pylint check does not
# require these imports to be absolute and descending from your superpackage.
import Integrator
from log_plus import log_plus, log_minus
import stat_trackers


class PLRsearch(object):
    """A class to encapsulate data relevant for search method.

    The context is performance testing of packet processing systems.
    The system, when being offered a steady stream of packets,
    can process some of them successfully, other are considered "lost".

    See docstring of the search method for algorithm description.

    Two constants are stored as class fields for speed.

    Method othed than search (and than __init__)
    are just internal code structure.
    TODO: Those method names should start with underscore then.
    """

    xerfcx_limit = math.pow(math.acos(0), -0.5)
    log_xerfcx_10 = math.log(xerfcx_limit - math.exp(10) * erfcx(math.exp(10)))

    def __init__(
            self, measurer, trial_duration_per_trial, packet_loss_ratio_target,
            trial_number_offset=0, timeout=60.0, trace_enabled=False):
        """Store rate measurer and additional parameters.

        Also declare packet_loss_per_second_target field (float),
        to be initialized later.

        TODO: Copy AbstractMeasurer from MLRsearch.

        :param measurer: The measurer to call when searching.
        :param trial_duration_per_trial: Each trial has larger duration
            than the previous trial. This is the increment, in seconds.
        :param packet_loss_ratio_target: The algorithm tries to estimate
            the offered load leading to this ratio on average.
            Trial ratio is number of packets lost divided by packets offered.
        :param trial_number_offset: The "first" trial number will be 1+this.
            Use this to ensure first iterations have enough time to compute
            reasonable estimates for later trials to use.
        :param timeout: The search ends if it lasts more than this many seconds.
        :type measurer: MLRsearch.AbstractMeasurer
        :type trial_duration_per_trial: float
        :type packet_loss_ratio_target: float
        :type trial_number_offset: int
        :type timeout: float
        """
        self.measurer = measurer
        self.trial_duration_per_trial = trial_duration_per_trial
        self.packet_loss_ratio_target = packet_loss_ratio_target
        self.trial_number_offset = trial_number_offset
        self.timeout = timeout
        self.trace_enabled = trace_enabled

    def search(self, min_rate, max_rate):
        """Perform the search, return average and stdev for throughput estimate.

        Considering measurer and packet_loss_ratio_target (see __init__),
        find such an offered load (called critical load) that is expected
        to hit the target loss ratio in the limit of very long trial duration.
        As the system is probabilistic (and test duration is finite),
        the critical ratio is only estimated.
        Return the average and standard deviation of the estimate.

        In principle, this algorithm performs trial measurements,
        each with varied offered load (which is constant during the trial).
        During each measurement, Bayesian inference is performed
        on all the measurement results so far.
        When timeout is up, the last estimate is returned,
        else another trial is performed.

        It is assumed that the system under test, even though not deterministic,
        still follows the rule of large numbers. In another words,
        any growing set of measurements at a particular offered load
        will converge towards unique (for the given load) packet loss ratio.
        This means there is a deterministic (but unknown) function
        mapping the offered load to average loss ratio.
        This function is called loss function.
        This also assumes the average loss ratio
        does not depend on trial duration.

        The actual probability distribution of loss counts, achieving
        the average ratio on trials of various duration
        can be complicated (and can depend on offered load), but simply assuming
        Poisson distribution will make the algorithm converge.
        Binomial distribution would be more precise,
        but Poisson is more practical, as it effectively gives
        less information content to high ratio results.

        Even when applying other assumptions on the loss function
        (increasing function, limit zero ratio when load goes to zero,
        global upper limit on rate of packets processed), there are still
        too many different shapes of possible loss functions,
        which makes full Bayesian reasoning intractable.

        This implementation radically simplifies things by examining
        only two shapes, each with finitely many (in this case just two)
        parameters. In other words, two fitting functions
        (each with two parameters and one argument).
        When restricting model space to one of the two fitting functions,
        the Bayesian inference becomes tractable (even though it needs
        numerical integration from Integrator class).

        The first measurement is done at min_rate to help with convergence
        if max_rate measurements give loss below target.
        FIXME: Fix overflow error and really use min_rate.
        The second measurement is done at max_rate, next few measurements
        have offered load of previous load minus excess loss ratio.
        This simple rule is found to be good when offered loads
        so far are way above the critical rate. After few measurements,
        inference from fitting functions converges faster that the initial
        "optimistic" procedure.

        Offered loads close to (limiting) critical rate are the most useful,
        as linear approximation of the fitting function
        becomes good enough there (thus reducing the impact
        of the overall shape of fitting function).
        After several trials, usually one of the fitting functions
        has better predictions than the other one, but the algorithm
        does not track that. Simply, it uses the estimate average,
        alternating between the functions.

        The returned average and stdev is a combination of the two fitting
        estimates.

        TODO: Limit sample critical rates by max_rate
        to make avg and stdev more conservative.

        :param min_rate: Avoid measuring at offered loads below this,
            in packets per second.
        :param max_rate: Avoid measuring at offered loads above this,
            in packets per second.
        :type min_rate: float
        :type max_rate: float
        :returns: Average and stdev of critical load estimate.
        :rtype: 2-tuple of floats
        """
        stop_time = time.time() + self.timeout
        min_rate = float(min_rate)
        max_rate = float(max_rate)
        logging.info("Started search with min_rate %(min)r, max_rate %(max)r",
                     {"min": min_rate, "max": max_rate})
        trial_result_list = list()
        trial_number = self.trial_number_offset
        focus_trackers = (None, None)
        message = "Trial %(number)r computed avg %(avg)r stdev %(stdev)r"
        message += " stretch %(a1)r erf %(a2)r difference %(diff)r"
        message += " focus_trackers %(tracker)r"
        transmit_rate = (min_rate + max_rate) / 2.0
        while 1:
            trial_number += 1
            trial_duration = trial_number * self.trial_duration_per_trial
            results = self.measure_and_compute(
                trial_duration, transmit_rate, trial_result_list,
                min_rate, max_rate, focus_trackers)
            measurement, average, stdev, avg1, avg2, focus_trackers = results
            logging.info(message, {
                "number": trial_number, "avg": average, "stdev": stdev,
                "a1": avg1, "a2": avg2, "diff": avg2 - avg1,
                "tracker": focus_trackers})
            if stop_time <= time.time():
                return average, stdev
            trial_result_list.append(measurement)
            if (trial_number - self.trial_number_offset) <= 1:
                next_load = max_rate
            elif (trial_number - self.trial_number_offset) <= 3:
                next_load = (measurement.receive_rate
                             / (1.0 - self.packet_loss_ratio_target))
            else:
                next_load = avg1 if trial_number % 2 else avg2
            transmit_rate = min(max_rate, max(min_rate, next_load))

    @staticmethod
    def lfit_stretch(trace, load, mrr, spread):
        """Stretch-based fitting function.

        Return the logarithm of average packet loss per second
        when the load (argument) is offered to a system with given
        mrr and spread (parameters).
        Stretch function is 1/(1+Exp[-x]). The average itself is definite
        integral from zero to load, of shifted and x-scaled stretch function.
        As the integrator is sensitive to discontinuities,
        and it calls this function at large areas of parameter space,
        the implementation has to avoid rounding errors, overflows,
        and correctly approximate underflows.

        TODO: Explain how the high-level description
        has been converted into an implementation full of ifs.

        :param trace: A multiprocessing-friendly logging function (closure).
        :param load: Offered load (positive), in packets per second.
        :param mrr: Parameter of this fitting function, equal to limiting
            (positive) average number of packets received (as opposed to lost)
            when offered load is many spreads more than mrr.
        :param spread: The x-scaling parameter (positive). No nice semantics,
            roughly corresponds to size of "tail" for loads below mrr.
        :type trace: function (str, object) -> None
        :type load: float
        :type mrr: float
        :type spread: float
        :returns: Logarithm of average number of packets lost per second.
        :rtype: float
        """
        # TODO: chi is from https://en.wikipedia.org/wiki/Nondimensionalization
        chi = (load - mrr) / spread
        chi0 = -mrr / spread
#        trace("stretch: load", load)
#        trace("mrr", mrr)
#        trace("spread", spread)
#        trace("chi", chi)
#        trace("chi0", chi0)
        if chi > 0:
            log_lps = math.log(
                load - mrr + (log_plus(0, -chi) - log_plus(0, chi0)) * spread)
#            trace("big loss direct log_lps", log_lps)
        else:
            approx = (math.exp(chi) - math.exp(2 * chi) / 2) * spread
            if approx == 0.0:
                log_lps = chi
#                trace("small loss crude log_lps", log_lps)
                return log_lps
            third = math.exp(3 * chi) / 3 * spread
            if approx + third != approx + 2 * third:
                log_lps = math.log(
                    (log_plus(0, chi) - log_plus(0, chi0)) * spread)
#                trace("small loss direct log_lps", log_lps)
            else:
                log_lps = math.log(
                    approx - (math.exp(chi0) - math.exp(2 * chi0)) * spread)
#                trace("small loss approx log_lps", log_lps)
        return log_lps

    @staticmethod
    def lfit_erf(trace, load, mrr, spread):
        """Erf-based fitting function.

        Return the logarithm of average packet loss per second
        when the load (argument) is offered to a system with given
        mrr and spread (parameters).
        Erf function is Primitive function to normal distribution density.
        The average itself is definite integral from zero to load,
        of shifted and x-scaled erf function.
        As the integrator is sensitive to discontinuities,
        and it calls this function at large areas of parameter space,
        the implementation has to avoid rounding errors, overflows,
        and correctly approximate underflows.

        TODO: Explain how the high-level description
        has been converted into an implementation full of ifs.

        :param trace: A multiprocessing-friendly logging function (closure).
        :param load: Offered load (positive), in packets per second.
        :param mrr: Parameter of this fitting function, equal to limiting
            (positive) average number of packets received (as opposed to lost)
            when offered load is many spreads more than mrr.
        :param spread: The x-scaling parameter (positive). No nice semantics,
            roughly corresponds to size of "tail" for loads below mrr.
        :type trace: function (str, object) -> None
        :type load: float
        :type mrr: float
        :type spread: float
        :returns: Logarithm of average number of packets lost per second.
        :rtype: float
        """
        # Beware, this chi has the sign opposite to the stretch function chi.
        # TODO: The stretch sign is just to have less minuses. Worth changing?
        chi = (mrr - load) / spread
        chi0 = mrr / spread
#        trace("Erf: load", load)
#        trace("mrr", mrr)
#        trace("spread", spread)
#        trace("chi", chi)
#        trace("chi0", chi0)
        if chi >= -1.0:
#            trace("positive, b roughly bigger than m", None)
            if chi > math.exp(10):
                first = PLRsearch.log_xerfcx_10 + 2 * (math.log(chi) - 10)
#                trace("approximated first", first)
            else:
                first = math.log(PLRsearch.xerfcx_limit - chi * erfcx(chi))
#                trace("exact first", first)
            first -= chi * chi
            second = math.log(PLRsearch.xerfcx_limit - chi * erfcx(chi0))
            second -= chi0 * chi0
            intermediate = log_minus(first, second)
#            trace("first", first)
        else:
#            trace("negative, b roughly smaller than m", None)
            exp_first = PLRsearch.xerfcx_limit + chi * erfcx(-chi)
            exp_first *= math.exp(-chi * chi)
            exp_first -= 2 * chi
            # TODO: Why has the following line chi there (as opposed to chi0)?
            # In general the functions would be more readable if they explicitly
            #     return math.log(func(chi) - func(chi0))
            # for some function "func", at least for some branches.
            second = math.log(PLRsearch.xerfcx_limit - chi * erfcx(chi0))
            second -= chi0 * chi0
            intermediate = math.log(exp_first - math.exp(second))
#            trace("exp_first", exp_first)
#        trace("second", second)
#        trace("intermediate", intermediate)
        result = intermediate + math.log(spread) - math.log(erfc(-chi0))
#        trace("result", result)
        return result

    @staticmethod
    def find_critical_rate(
            trace, lfit_func, min_rate, max_rate, loss_ratio_target,
            mrr, spread):
        """Given ratio target and parameters, return the achieving offered load.

        This is basically an inverse function to lfit_func
        when parameters are fixed.
        Instead of implementing effective implementation
        of the inverse function, this implementation uses
        brute force binary search.

        The implementation uses binary search, bisecting until the critical
        load is found (or interval becoming degenerate).
        This implementation assures min and max rate limits are honored.

        TODO: Use at some method with faster convergence?

        :param trace: A multiprocessing-friendly logging function (closure).
        :param lfit_func: Fitting function, typically lfit_spread or lfit_erf.
        :param min_rate: Lower bound for binary search [pps].
        :param max_rate: Upper bound for binary search [pps].
        :param loss_ratio_target: Fitting function should return loss rate
            giving this ratio at the returned load and parameters [1].
        :param mrr: The mrr parameter for the fitting function [pps].
        :param spread: The spread parameter for the fittinmg function [pps].
        :type trace: function (str, object) -> None
        :type lfit_func: Function from 3 floats to float.
        :type min_rate: float
        :type max_rate: float
        :type log_lps_target: float
        :type mrr: float
        :type spread: float
        :returns: Load [pps] which achieves the target with given parameters.
        :rtype: float
        """
#        trace("Finding critical rate for loss_ratio_target", loss_ratio_target)
        rate_lo = min_rate
        rate_hi = max_rate
        loss_ratio = -1
        while loss_ratio != loss_ratio_target:
            rate = (rate_hi + rate_lo) / 2.0
            if rate == rate_hi or rate == rate_lo:
                break
            loss_rate = math.exp(lfit_func(trace, rate, mrr, spread))
            loss_ratio = loss_rate / rate
            if loss_ratio > loss_ratio_target:
#                trace("halving down", rate)
                rate_hi = rate
            elif loss_ratio < loss_ratio_target:
#                trace("halving up", rate)
                rate_lo = rate
#        trace("found", rate)
        return rate

    @staticmethod
    def log_weight(trace, lfit_func, trial_result_list, mrr, spread):
        """Return log of weight of trial results by the function and parameters.

        Integrator assumes uniform distribution, but over different parameters.
        Weight and likelihood are used interchangeably here anyway.

        Each trial has an offered load, a duration and a loss count.
        Fitting function is used to compute the average loss per second.
        Poisson distribution (with average loss per trial) is used
        to get likelihood of one trial result, the overal likelihood is product.
        As likelihoods can be extremely small, logarithms are tracked instead.

        TODO: Copy ReceiveRateMeasurement from MLRsearch.

        :param trace: A multiprocessing-friendly logging function (closure).
        :param lfit_func: Fitting function, typically lfit_spread or lfit_erf.
        :param result_list: List of trial measurement results.
        :param mrr: The mrr parameter for the fitting function.
        :param spread: The spread parameter for the fittinmg function.
        :type trace: function (str, object) -> None
        :type lfit_func: Function from 3 floats to float.
        :type result_list: list of MLRsearch.ReceiveRateMeasurement
        :type mrr: float
        :type spread: float
        :returns: Logarithm of result weight for given function and parameters.
        :rtype: float
        """
        log_likelihood = 0.0
#        trace("log_weight for mrr", mrr)
#        trace("spread", spread)
        for result in trial_result_list:
#            trace("for tr", result.target_tr)
#            trace("lc", result.loss_count)
#            trace("d", result.duration)
            log_avg_loss_per_second = lfit_func(
                trace, result.target_tr, mrr, spread)
            log_avg_loss_per_trial = (
                log_avg_loss_per_second + math.log(result.duration))
            # Poisson probability computation works nice for logarithms.
            log_trial_likelihood = (
                result.loss_count * log_avg_loss_per_trial
                - math.exp(log_avg_loss_per_trial))
            log_trial_likelihood -= math.lgamma(1 + result.loss_count)
            log_likelihood += log_trial_likelihood
#            trace("avg_loss_per_trial", math.exp(log_avg_loss_per_trial))
#            trace("log_trial_likelihood", log_trial_likelihood)
        return log_likelihood

    # FIXME: Refactor (somehow) so pylint stops complaining about
    # too many local variables.
    # Some work already done in subsequent changes.
    def measure_and_compute(
            self, trial_duration, transmit_rate, trial_result_list,
            min_rate, max_rate, focus_trackers, max_samples=None):
        """Perform both measurement and computation at once.

        High level steps: Prepare and launch computation worker processes,
        perform the measurement, stop computation and combine results.

        Integrator needs a specific function to process (-1, 1) parameters.
        As our fitting functions use dimensional parameters,
        so a transformation is performed, resulting in a specific prior
        distribution over the dimensional parameters.
        Maximal rate (line rate) is needed for that transformation.

        Two fitting functions are used, computation is started
        on temporary worker process per fitting function. After the measurement,
        Average and stdev of the critical rate (not log) of each worker
        are combined and returned. Raw averages are also returned,
        offered load for next iteration is chosen from them.
        The idea is that one fitting function might be fitting much better,
        measurements at its avg are best for relevant results (for both),
        but we do not know which fitting function it is.

        TODO: Define class for focus tracker, so that fields are documented.
        TODO: Define class for result object, so that fields are documented.
        TODO: More processes to the slower fitting function?
        TODO: Re-use processes, instead creating on each computation.
        TODO: As only one result is needed fresh, figure out a way
        how to keep the other worker running. This will alow shorter
        duration per trial. Special handling at first and last measurement
        will be needed (to properly initialize and to properly combine results).

        :param trial_duration: Length of the measurement in seconds.
        :param transmit_rate: Offered load in packets per second.
        :param trial_result_list: Results of previous measurements.
        :param min_rate: Theoretic minimum of possible ofered load.
        :param max_rate: Theoretic maximum of possible ofered load.
        :param focus_trackers: Hints to speed up the numeric computation.
        :param max_samples: Limit for integrator samples, for debugging.
        :type trial_duration: float
        :type transmit_rate: float
        :type trial_result_list: list of MLRsearch.ReceiveRateMeasurement
        :type min_rate: float
        :type max_rate: float
        :type focus_trackers: 4-tuple of gaussian positions and covariances
        :type max_samples: None or int
        :returns: Measurement and computation results.
        :rtype: 6-tuple: ReceiveRateMeasurement, floats, focus tracker.
        """
        logging.debug(
            "measure_and_compute started with self %(self)r, trial_duration "
            + "%(dur)r, transmit_rate %(tr)r, trial_result_list %(trl)r, "
            + "max_rate %(mr)r, focus_trackers %(tracker)r, max_samples %(ms)r",
            {"self": self, "dur": trial_duration, "tr": transmit_rate,
             "trl": trial_result_list, "mr": max_rate, "tracker": focus_trackers,
             "ms": max_samples})
        # Preparation phase.
        dimension = 2
        stretch_focus_tracker, erf_focus_tracker = focus_trackers
        def start_computing(fitting_function, focus_tracker):
            """Just a block of code to be used for each fitting function.

            Define function for integrator, create process and pipe ends,
            start computation, return the boss pipe end.

            :param fitting_function: lfit_erf or lfit_stretch.
            :param bias_avg: Tuple of floats to start searching around.
            :param bias_cov: Covariance matrix defining initial focus shape.
            :type fitting_function: Function from 3 floats to float.
            :type bias_avg: 2-tuple of floats
            :type bias_cov: 2-tuple of 2-tuples of floats
            :returns: Boss end of communication pipe.
            :rtype: multiprocessing.Connection
            """
            def value_logweight_func(trace, x_mrr, x_spread):
                """Return log of critical rate and log of likelihood.

                This is a closure. The ancestor function got
                trial_result_list as a parameter, and we are accessing it.
                As integrator has strict conditions on function signature,
                trial_result_list cannot be an explicit argument
                of the current function.
                This is also why we have to define this closure
                at each invocation of the ancestor function anew.

                The dimensional spread parameter is the (dimensional) mrr
                raised to the power of x_spread scaled to interval (0, 1).
                The dimensional mrr parameter distribution has shape of
                1/(1+x^2), but x==1 corresponds to max_rate
                and 1.0 pps is added to avoid numerical problems in fitting
                functions.

                TODO: x^-2 (for x>1.0) might be simpler/nicer prior.

                :param trace: A multiprocessing-friendly logging function (closure).
                :param x_mrr: The first dimensionless param
                    from (-1, 1) interval.
                :param x_spread: The second dimensionless param
                    from (-1, 1) interval.
                :type trace: function (str, object) -> None
                :type x_mrr: float
                :type x_spread: float
                :returns: Log of critical rate [pps] and log of likelihood.
                :rtype: 2-tuple of float
                """
                mrr = max_rate * (1.0 / (x_mrr + 1.0) - 0.5) + 1.0
                spread = math.exp((x_spread + 1.0) / 2.0 * math.log(mrr))
                logweight = self.log_weight(
                    trace, fitting_function, trial_result_list, mrr, spread)
                value = math.log(self.find_critical_rate(
                    trace, fitting_function, min_rate, max_rate,
                    self.packet_loss_ratio_target, mrr, spread))
                return value, logweight
            dilled_function = dill.dumps(value_logweight_func)
            boss_pipe_end, worker_pipe_end = multiprocessing.Pipe()
            boss_pipe_end.send(
                (dimension, dilled_function, focus_tracker, max_samples))
            worker = multiprocessing.Process(
                target=Integrator.try_estimate_nd, args=(
                    worker_pipe_end, 10.0, self.trace_enabled))
            worker.daemon = True
            worker.start()
            return boss_pipe_end
        erf_pipe = start_computing(
            self.lfit_erf, erf_focus_tracker)
        stretch_pipe = start_computing(
            self.lfit_stretch, stretch_focus_tracker)
        # Measurement phase.
        measurement = self.measurer.measure(trial_duration, transmit_rate)
        # Processing phase.
        def stop_computing(name, pipe):
            """Just a block of code to be used for each worker.

            Send stop object, poll for result, then either
            unpack response, log messages and return, or raise traceback.

            TODO: Define class/structure for the return value?

            :param name: Human friendly worker identifier for logging purposes.
            :param pipe: Boss end of connection towards worker to stop.
            :type name: str
            :type pipe: multiprocessing.Connection
            :returns: Average and stdev of the computed quantity,
                averages and covariance matrix to start with in next iteration.
            :rtype: 4-tuple of float, float, vector and matrix.
            """
            pipe.send(None)
            if not pipe.poll(10.0):
                raise RuntimeError(
                    "Worker {name} did not finish!".format(name=name))
            result_or_traceback = pipe.recv()
            try:
                value_tracker, focus_tracker, debug_list, trace_list = (
                    result_or_traceback)
            except ValueError:
                raise RuntimeError(
                    "Worker {name} failed with the following traceback:\n{tr}"
                    .format(name=name, tr=result_or_traceback))
            logging.info("Logs from worker {name}:".format(name=name))
            for message in debug_list:
                logging.info(message)
            for message in trace_list:
                logging.debug(message)
            print "DEBUG trackers: value {val!r} focus {foc!r}".format(
                val=value_tracker, foc=focus_tracker)
            return value_tracker, focus_tracker
        stretch_value_tracker = stat_trackers.ScalarDualStatTracker()
        stretch_value_tracker.add(1, 0).add(2, 0)
        stretch_value_tracker, stretch_focus_tracker = (
            stop_computing("stretch", stretch_pipe))
        erf_value_tracker, erf_focus_tracker = (
            stop_computing("erf", erf_pipe))
        stretch_avg = stretch_value_tracker.average
        erf_avg = erf_value_tracker.average
        # FIXME: Take into account secondary stats.
        stretch_stdev = math.exp(stretch_value_tracker.log_variance / 2)
        erf_stdev = math.exp(erf_value_tracker.log_variance / 2)
        avg = math.exp((stretch_avg + erf_avg) / 2.0)
        var = (stretch_stdev * stretch_stdev + erf_stdev * erf_stdev) / 2.0
        var += (stretch_avg - erf_avg) * (stretch_avg - erf_avg) / 4.0
        stdev = avg * math.sqrt(var)
        focus_trackers = (stretch_focus_tracker, erf_focus_tracker)
        return (
            measurement, avg, stdev, math.exp(stretch_avg),
            math.exp(erf_avg), focus_trackers)
