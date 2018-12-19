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

"""Module holding PLRsearch class."""

import logging
import math
import multiprocessing
import random
import time

import dill
from scipy.special import erfcx, erfc

import Integrator
from log_plus import log_plus, log_minus


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

    TODO: Figure out how to replace #print with logging
    without slowing down too much.
    """

    xerfcx_limit = math.pow(math.acos(0), -0.5)
    log_xerfcx_10 = math.log(xerfcx_limit - math.exp(10) * erfcx(math.exp(10)))

    def __init__(
            self, measurer, trial_duration_per_trial, packet_loss_ratio_target,
            trial_number_offset=0, timeout=60.0):
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

        TODO: If measurement at max_rate is already below target loss rate,
        the algorithm always measures at max_rate, and likelihood
        no longer has single maximum, leading to "random" estimates.
        Find a way to avoid that.

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
        trial_result_list = list()
        trial_number = self.trial_number_offset
        integrator_data = (None, None, None, None)
        message = "Trial {number} computed avg {avg} stdev {stdev}"
        message += " stretch {a1} erf {a2} difference {d}"
        message += " integrator_data {id!r}"
        transmit_rate = (min_rate + max_rate) / 2.0
        while 1:
            trial_number += 1
            trial_duration = trial_number * self.trial_duration_per_trial
            results = self.measure_and_compute(
                trial_duration, transmit_rate, trial_result_list, max_rate,
                integrator_data)
            measurement, average, stdev, avg1, avg2, integrator_data = results
            logging.info(message.format(
                number=trial_number, avg=average, stdev=stdev,
                a1=avg1, a2=avg2, d=avg2-avg1, id=integrator_data))
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
    def lfit_stretch(load, mrr, spread):
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

        :param load: Offered load (positive), in packets per second.
        :param mrr: Parameter of this fitting function, equal to limiting
            (positive) average number of packets received (as opposed to lost)
            when offered load is many spreads more than mrr.
        :param spread: The x-scaling parameter (positive). No nice semantics,
            roughly corresponds to size of "tail" for loads below mrr.
        :type load: float
        :type mrr: float
        :type spread: float
        :returns: Logarithm of average number of packets lost per second.
        :rtype: float
        """
        # TODO: chi is from https://en.wikipedia.org/wiki/Nondimensionalization
        chi = (load - mrr) / spread
        chi0 = -mrr / spread
#        print "load", load, "mrr", mrr, "spread", spread, "chi", chi
        if chi > 0:
            log_lps = math.log(
                load - mrr + (log_plus(0, -chi) - log_plus(0, chi0)) * spread)
#            print "big loss direct log_lps", log_lps
        else:
            approx = (math.exp(chi) - math.exp(2 * chi) / 2) * spread
            if approx == 0.0:
                log_lps = chi
#                print "small loss crude log_lps", log_lps
                return log_lps
            third = math.exp(3 * chi) / 3 * spread
            if approx + third != approx + 2 * third:
                log_lps = math.log(
                    (log_plus(0, chi) - log_plus(0, chi0)) * spread)
#                print "small loss direct log_lps", log_lps
            else:
                log_lps = math.log(
                    approx - (math.exp(chi0) - math.exp(2 * chi0)) * spread)
#                print "small loss approx log_lps", log_lps
        return log_lps

    @staticmethod
    def lfit_erf(load, mrr, spread):
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

        :param load: Offered load (positive), in packets per second.
        :param mrr: Parameter of this fitting function, equal to limiting
            (positive) average number of packets received (as opposed to lost)
            when offered load is many spreads more than mrr.
        :param spread: The x-scaling parameter (positive). No nice semantics,
            roughly corresponds to size of "tail" for loads below mrr.
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
#        print "load", load, "mrr", mrr, "spread", spread,
#        print "chi", chi, "chi0", chi0
        if chi >= -1.0:
#            print "positive, b ~> m"
            if chi > math.exp(10):
                first = PLRsearch.log_xerfcx_10 + 2 * (math.log(chi) - 10)
#                print "approximated"
            else:
                first = math.log(PLRsearch.xerfcx_limit - chi * erfcx(chi))
#                print "exact"
            first -= chi * chi
            second = math.log(PLRsearch.xerfcx_limit - chi * erfcx(chi0))
            second -= chi0 * chi0
            intermediate = log_minus(first, second)
#            print "first", first, "second", second,
#            print "intermediate", intermediate
        else:
#            print "negative, b ~< m"
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
#            print "exp_first", exp_first, "second", second,
#            print "intermediate", intermediate
        result = intermediate + math.log(spread) - math.log(erfc(-chi0))
#        print "lfit erf result", result
        return result

    @staticmethod
    def find_critical_rate(lfit_func, log_lps_target, mrr, spread):
        """Given lps target and parameters, return the achieving offered load.

        This is basically an inverse function to lfit_func
        when parameters are fixed.
        Instead of implementing effective implementation
        of the inverse function, this implementation uses
        brute force binary search.
        The search starts at an arbitrary offered load,
        uses exponential search to find the other bound
        and then bisecting until the load is found (or interval
        becoming degenerate).

        TODO: Use at least some method with faster convergence.

        :param lfit_func: Fitting function, typically lfit_spread or lfit_erf.
        :param log_lps_target: Fitting function should return this
            at the returned load and parameters.
        :param mrr: The mrr parameter for the fitting function.
        :param spread: The spread parameter for the fittinmg function.
        :type lfit_func: Function from 3 floats to float.
        :type log_lps_target: float
        :type mrr: float
        :type spread: float
        :returns: Load [pps] which achieves the target with given parameters.
        :rtype: float
        """
        # TODO: Should we make the initial rate configurable?
        rate = 10000000.0
        log_loss = lfit_func(rate, mrr, spread)
        if log_loss == log_lps_target:
            return rate
        # Exponential search part.
        if log_loss > log_lps_target:
            rate_hi = rate
            while 1:
                rate_lo = rate_hi / 2.0
                log_loss = lfit_func(rate_lo, mrr, spread)
                if log_loss > log_lps_target:
                    rate_hi = rate_lo
                    continue
                if log_loss == log_lps_target:
                    return rate_lo
                break
        else:
            rate_lo = rate
            while 1:
                rate_hi = rate_lo * 2.0
                log_loss = lfit_func(rate_hi, mrr, spread)
                if log_loss < log_lps_target:
                    rate_lo = rate_hi
                    continue
                if log_loss == log_lps_target:
                    return rate_hi
                break
        # Binary search part.
        while rate_hi != rate_lo:
            rate = (rate_hi + rate_lo) / 2.0
            log_loss = lfit_func(rate, mrr, spread)
            if rate == rate_hi or rate == rate_lo or log_loss == log_lps_target:
#                print "found", rate
                return rate
            if log_loss > log_lps_target:
                rate_hi = rate
            else:
                rate_lo = rate

    @staticmethod
    def log_weight(lfit_func, trial_result_list, mrr, spread):
        """Return log of weight of trial results by the function and parameters.

        Integrator assumes uniform distribution, but over different parameters.
        Weight and likelihood are used interchangeably here anyway.

        Each trial has an offered load, a duration and a loss count.
        Fitting function is used to compute the average loss per second.
        Poisson distribution (with average loss per trial) is used
        to get likelihood of one trial result, the overal likelihood is product.
        As likelihoods can be extremely small, logarithms are tracked instead.

        TODO: Copy ReceiveRateMeasurement from MLRsearch.

        :param lfit_func: Fitting function, typically lfit_spread or lfit_erf.
        :param result_list: List of trial measurement results.
        :param mrr: The mrr parameter for the fitting function.
        :param spread: The spread parameter for the fittinmg function.
        :type lfit_func: Function from 3 floats to float.
        :type result_list: list of MLRsearch.ReceiveRateMeasurement
        :type mrr: float
        :type spread: float
        :returns: Logarithm of result weight for given function and parameters.
        :rtype: float
        """
        log_likelihood = 0.0
        for result in trial_result_list:
#            print "DEBUG for tr", result.target_tr,
#            print "lc", result.loss_count, "d", result.duration
            log_avg_loss_per_second = lfit_func(result.target_tr, mrr, spread)
            log_avg_loss_per_trial = (
                log_avg_loss_per_second + math.log(result.duration))
            # Poisson probability computation works nice for logarithms.
            log_trial_likelihood = (
                result.loss_count * log_avg_loss_per_trial
                - math.exp(log_avg_loss_per_trial))
            log_trial_likelihood -= math.lgamma(1 + result.loss_count)
            log_likelihood += log_trial_likelihood
#            print "log_avg_loss_per_second", log_avg_loss_per_second
#            print "log_avg_loss_per_trial", log_avg_loss_per_trial
#            print "avg_loss_per_trial", math.exp(log_avg_loss_per_trial)
#            print "log_trial_likelihood", log_trial_likelihood
#            print "log_likelihood", log_likelihood
#        print "returning log_likelihood", log_likelihood
        return log_likelihood

    def measure_and_compute(
            self, trial_duration, transmit_rate,
            trial_result_list, max_rate, integrator_data):
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

        TODO: Define class for integrator data, so that fields are documented.
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
        :param max_rate: Theoretic maximum of possible ofered load.
        :param integrator_data: Hints to speed up the numeric computation.
        :type trial_duration: float
        :type transmit_rate: float
        :type trial_result_list: list of MLRsearch.ReceiveRateMeasurement
        :type max_rate: float
        :type integrator_data: 4-tuple of gaussian positions and covariances
        :returns: Measurement and computation results.
        :rtype: 6-tuple: ReceiveRateMeasurement, floats, integrator data.
        """
        # Preparation phase.
        dimension = 2
        stretch_bias_avg, erf_bias_avg, stretch_bias_cov, erf_bias_cov = (
            integrator_data)
        random.seed(0)
        packet_loss_per_second_target = (
            transmit_rate * self.packet_loss_ratio_target)
        def start_computing(fitting_function, bias_avg, bias_cov):
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
            def value_logweight_func(x_mrr, x_spread):
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

                :param x_mrr: The first dimensionless param
                    from (-1, 1) interval.
                :param x_spread: The second dimensionless param
                    from (-1, 1) interval.
                :returns: Log of critical rate [pps] and log of likelihood.
                :rtype: 2-tuple of float
                """
                mrr = max_rate * (1.0 / (x_mrr + 1.0) - 0.5) + 1.0
                spread = math.exp((x_spread + 1.0) / 2.0 * math.log(mrr))
#                print "mrr", mrr, "spread", spread
                logweight = self.log_weight(
                    fitting_function, trial_result_list, mrr, spread)
                value = math.log(self.find_critical_rate(
                    fitting_function,
                    math.log(packet_loss_per_second_target), mrr, spread))
                return value, logweight
            dilled_function = dill.dumps(value_logweight_func)
            boss_pipe_end, worker_pipe_end = multiprocessing.Pipe()
            boss_pipe_end.send(
                (dimension, dilled_function, bias_avg, bias_cov))
            worker = multiprocessing.Process(
                target=Integrator.try_estimate_nd, args=(worker_pipe_end,))
            worker.daemon = True
            worker.start()
            return boss_pipe_end
        erf_pipe = start_computing(
            self.lfit_erf, erf_bias_avg, erf_bias_cov)
#        stretch_pipe = start_computing(
#            self.lfit_stretch, stretch_bias_avg, stretch_bias_cov)
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
            if not pipe.poll(1.0):
                raise RuntimeError(
                    "Worker {name} did not finish!".format(name=name))
            result_or_traceback = pipe.recv()
            try:
                avg, stdev, bias_avg, bias_cov, debug_list, trace_list = (
                    result_or_traceback)
            except ValueError:
                raise RuntimeError(
                    "Worker {name} failed with the following traceback:\n{tr}"
                    .format(name=name, tr=result_or_traceback))
            logging.info("Logs from worker {name}:".format(name=name))
            for message in debug_list:
                logging.debug(message)
            for message in trace_list:
                logging.trace(message)
            return avg, stdev, bias_avg, bias_cov
        stretch_avg, stretch_stdev, stretch_bias_avg, stretch_bias_cov = (
            10.0, 0.1, [0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]])
#            stop_computing("stretch", stretch_pipe))
        erf_avg, erf_stdev, erf_bias_avg, erf_bias_cov = (
            stop_computing("erf", erf_pipe))
        avg = math.exp((stretch_avg + erf_avg) / 2.0)
        var = (stretch_stdev * stretch_stdev + erf_stdev * erf_stdev) / 2.0
        var += (stretch_avg - erf_avg) * (stretch_avg - erf_avg) / 4.0
        stdev = avg * math.sqrt(var)
        integrator_data = (
            stretch_bias_avg, erf_bias_avg, stretch_bias_cov, erf_bias_cov)
        return (
            measurement, avg, stdev, math.exp(stretch_avg),
            math.exp(erf_avg), integrator_data)
