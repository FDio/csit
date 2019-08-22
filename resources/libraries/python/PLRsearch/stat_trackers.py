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

"""Module for tracking average and variance for data of weighted samples.

See log_plus for an explanation why None acts as a special case "float" number.

TODO: Current implementation sets zero averages on empty tracker.
Should we set None instead?

TODO: Implement __str__ and __repr__ for easier debugging.
"""

import copy
import math

import numpy

# TODO: Teach FD.io CSIT to use multiple dirs in PYTHONPATH,
# then switch to absolute imports within PLRsearch package.
# Current usage of relative imports is just a short term workaround.
from .log_plus import log_plus, safe_exp


class ScalarStatTracker(object):
    """Class for tracking one-dimensional samples.

    Variance of one-dimensional data cannot be negative,
    so this class avoids possible underflows by tracking logarithm
    of the variance instead.

    Similarly, sum of weights is also tracked as a logarithm.
    """

    def __init__(self, log_sum_weight=None, average=0.0, log_variance=None):
        """Initialize new tracker instance, empty by default.

        :param log_sum_weight: Natural logarithm of sum of weights
            of samples so far. Default: None (as log of 0.0).
        :param average: Weighted average of the samples. Default: 0.0
        :param log_variance: Natural logarithm of variance.
            Default: None (as log of 0.0).
        :type log_sum_weight: float or None
        :type average: float
        :type log_variance: float or None
        """
        self.log_sum_weight = log_sum_weight
        self.average = average
        self.log_variance = log_variance

    def __repr__(self):
        """Return string, which interpreted constructs state of self.

        :returns: Expression contructing an equivalent instance.
        :rtype: str
        """
        return ("ScalarStatTracker(log_sum_weight={lsw!r},average={a!r},"
                "log_variance={lv!r})".format(
                    lsw=self.log_sum_weight, a=self.average,
                    lv=self.log_variance))

    def copy(self):
        """Return new ScalarStatTracker instance with the same state as self.

        The point of this method is the return type, instances of subclasses
        can get rid of their additional data this way.

        :returns: New instance with the same core state.
        :rtype: ScalarStatTracker
        """
        return ScalarStatTracker(
            self.log_sum_weight, self.average, self.log_variance)

    def add(self, scalar_value, log_weight=0.0):
        """Return updated stats corresponding to addition of another sample.

        :param scalar_value: The scalar value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type scalar_value: float
        :type log_weight: float
        :returns: Updated self.
        :rtype: ScalarStatTracker
        """
        old_log_sum_weight = self.log_sum_weight
        if old_log_sum_weight is None:
            # First sample.
            self.log_sum_weight = log_weight
            self.average = scalar_value
            return self
        old_average = self.average
        log_variance = self.log_variance
        new_log_sum_weight = log_plus(old_log_sum_weight, log_weight)
        log_sample_ratio = log_weight - new_log_sum_weight
        sample_ratio = math.exp(log_sample_ratio)
        shift = scalar_value - old_average
        new_average = old_average + shift * sample_ratio
        # The log_variance is updated in-place (instead of new_ vs old_)
        # because of if-s detecting None-s where the value does not change.
        absolute_shift = abs(shift)
        if absolute_shift > 0.0:
            log_square_shift = 2 * math.log(absolute_shift)
            log_variance = log_plus(
                log_variance, log_square_shift + log_sample_ratio)
        if log_variance is not None:
            log_variance += old_log_sum_weight - new_log_sum_weight
        self.log_sum_weight = new_log_sum_weight
        self.average = new_average
        self.log_variance = log_variance
        return self


class ScalarDualStatTracker(ScalarStatTracker):
    """Class for tracking one-dimensional samples, offering dual stats.

    It means that instead of just primary stats (identical to what
    ScalarStatTracker offers, that is why this is its subclass),
    this tracker allso offers secondary stats.
    Secondary stats are scalar stats that track the same data,
    except that the most weighty (or later if tied) sample is not considered.

    Users can analyze how do secondary stats differ from the primary ones,
    and based on that decide whether they processed "enough" data.
    One typical use is for Monte Carlo integrator to decide whether
    the partial sums so far are reliable enough.
    """

    def __init__(
            self, log_sum_weight=None, average=0.0, log_variance=None,
            log_sum_secondary_weight=None, secondary_average=0.0,
            log_secondary_variance=None, max_log_weight=None):
        """Initialize new tracker instance, empty by default.

        :param log_sum_weight: Natural logarithm of sum of weights
            of samples so far. Default: None (as log of 0.0).
        :param average: Weighted average of the samples. Default: 0.0
        :param log_variance: Natural logarithm of variance.
            Default: None (as log of 0.0).
        :param log_sum_secondary_weight: Natural logarithm of sum of weights
            of samples so far except weightest one.
            Default: None (as log of 0.0).
        :param secondary_average: Weighted average of the samples
            except the weightest one. Default: 0.0
        :param log_variance: Natural logarithm of variance od samples
            except the weightest one. Default: None (as log of 0.0).
        :param max_log_weight: Natural logarithm of weight of sample
            counted in primary but not secondary stats.
            Default: None (as log of 0.0).
        :type log_sum_weight: float or None
        :type average: float
        :type log_variance: float or None
        :type log_sum_secondary_weight: float or None
        :type secondary_average: float
        :type log_secondary_variance: float or None
        :type max_log_weight: float or None
        """
        # Not using super() as the constructor signature is different,
        # so in case of diamond inheritance mismatch would be probable.
        ScalarStatTracker.__init__(self, log_sum_weight, average, log_variance)
        self.secondary = ScalarStatTracker(
            log_sum_secondary_weight, secondary_average, log_secondary_variance)
        self.max_log_weight = max_log_weight

    def __repr__(self):
        """Return string, which interpreted constructs state of self.

        :returns: Expression contructing an equivalent instance.
        :rtype: str
        """
        sec = self.secondary
        return (
            "ScalarDualStatTracker(log_sum_weight={lsw!r},average={a!r},"
            "log_variance={lv!r},log_sum_secondary_weight={lssw!r},"
            "secondary_average={sa!r},log_secondary_variance={lsv!r},"
            "max_log_weight={mlw!r})".format(
                lsw=self.log_sum_weight, a=self.average, lv=self.log_variance,
                lssw=sec.log_sum_weight, sa=sec.average, lsv=sec.log_variance,
                mlw=self.max_log_weight))

    def add(self, scalar_value, log_weight=0.0):
        """Return updated both stats after addition of another sample.

        :param scalar_value: The scalar value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type scalar_value: float
        :type log_weight: float
        :returns: Updated self.
        :rtype: ScalarDualStatTracker
        """
        # Using super() as copy() and add() are not expected to change
        # signature, so this way diamond inheritance will be supported.
        primary = super(ScalarDualStatTracker, self)
        if self.max_log_weight is None or log_weight >= self.max_log_weight:
            self.max_log_weight = log_weight
            self.secondary = primary.copy()
        else:
            self.secondary.add(scalar_value, log_weight)
        primary.add(scalar_value, log_weight)
        return self


    def get_pessimistic_variance(self):
        """Return estimate of variance reflecting weight effects.

        Typical scenario is the primary tracker dominated by a single sample.
        In worse case, secondary tracker is also dominated by
        a single (but different) sample.

        Current implementation simply returns variance of average
        of the two trackers, as if they were independent.

        :returns: Pessimistic estimate of variance (not stdev, no log).
        :rtype: float
        """
        var_primary = safe_exp(self.log_variance)
        var_secondary = safe_exp(self.secondary.log_variance)
        var_combined = (var_primary + var_secondary) / 2
        avg_half_diff = (self.average - self.secondary.average) / 2
        var_combined += avg_half_diff * avg_half_diff
        return var_combined


class VectorStatTracker(object):
    """Class for tracking multi-dimensional samples.

    Contrary to one-dimensional data, multi-dimensional covariance matrix
    contains off-diagonal elements which can be negative.

    But, sum of weights is never negative, so it is tracked as a logarithm.

    The code assumes every method gets arguments with correct dimensionality
    as set in constructor. No checks are performed (for performance reasons).

    TODO: Should we provide a subclass with the dimensionality checks?
    """

    def __init__(
            self, dimension=2, log_sum_weight=None, averages=None,
            covariance_matrix=None):
        """Initialize new tracker instance, two-dimenstional empty by default.

        If any of latter two arguments is None, it means
        the tracker state is invalid. Use reset method
        to create empty tracker of constructed dimentionality.

        :param dimension: Number of scalar components of samples.
        :param log_sum_weight: Natural logarithm of sum of weights
            of samples so far. Default: None (as log of 0.0).
        :param averages: Weighted average of the samples.
            Default: None
        :param covariance_matrix: Variance matrix elements.
            Default: None
        :type log_sum_weight: float or None
        :type averages: None or tuple of float
        :type covariance_matrix: None or tuple of tuple of float
        """
        self.dimension = dimension
        self.log_sum_weight = log_sum_weight
        self.averages = averages
        self.covariance_matrix = covariance_matrix

    def __repr__(self):
        """Return string, which interpreted constructs state of self.

        :returns: Expression contructing an equivalent instance.
        :rtype: str
        """
        return (
            "VectorStatTracker(dimension={d!r},log_sum_weight={lsw!r},"
            "averages={a!r},covariance_matrix={cm!r})".format(
                d=self.dimension, lsw=self.log_sum_weight, a=self.averages,
                cm=self.covariance_matrix))

    def copy(self):
        """Return new instance with the same state as self.

        The main usage is to simplify debugging. This method allows
        to store the old state, while self continues to track towards new state.

        :returns: Created tracker instance.
        :rtype: VectorStatTracker
        """
        return VectorStatTracker(
            self.dimension, self.log_sum_weight, self.averages[:],
            copy.deepcopy(self.covariance_matrix))

    def reset(self):
        """Return state set to empty data of proper dimensionality.

        :returns: Updated self.
        :rtype: VectorStatTracker
        """
        self.averages = [0.0 for _ in range(self.dimension)]
        # TODO: Examine whether we can gain speed by tracking triangle only.
        self.covariance_matrix = [[0.0 for _ in range(self.dimension)]
                                  for _ in range(self.dimension)]
        # TODO: In Python3, list comprehensions are generators,
        # so they are not indexable. Put list() when converting.
        return self

    def unit_reset(self):
        """Reset state but use unit matric as covariance.

        :returns: Updated self.
        :rtype: VectorStatTracker
        """
        self.reset()
        for index in range(self.dimension):
            self.covariance_matrix[index][index] = 1.0
        return self

    def add_get_shift(self, vector_value, log_weight=0.0):
        """Return shift and update state to addition of another sample.

        Shift is the vector from old average to new sample.
        For most callers, returning shift is more useful than returning self.

        :param vector_value: The value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type vector_value: iterable of float
        :type log_weight: float
        :returns: Shift vector
        :rtype: list of float
        """
        dimension = self.dimension
        old_log_sum_weight = self.log_sum_weight
        old_averages = self.averages
        if not old_averages:
            shift = [0.0 for index in range(dimension)]
        else:
            shift = [vector_value[index] - old_averages[index]
                     for index in range(dimension)]
        if old_log_sum_weight is None:
            # First sample.
            self.log_sum_weight = log_weight
            self.averages = [vector_value[index] for index in range(dimension)]
            # Not touching covariance matrix.
            return shift
        covariance_matrix = self.covariance_matrix
        new_log_sum_weight = log_plus(old_log_sum_weight, log_weight)
        data_ratio = math.exp(old_log_sum_weight - new_log_sum_weight)
        sample_ratio = math.exp(log_weight - new_log_sum_weight)
        new_averages = [old_averages[index] + shift[index] * sample_ratio
                        for index in range(dimension)]
        # It is easier to update covariance matrix in-place.
        for second in range(dimension):
            for first in range(dimension):
                element = covariance_matrix[first][second]
                element += shift[first] * shift[second] * sample_ratio
                element *= data_ratio
                covariance_matrix[first][second] = element
        self.log_sum_weight = new_log_sum_weight
        self.averages = new_averages
        # self.covariance_matrix still points to the object we updated in-place.
        return shift

    # TODO: There are some uses for such a vector tracker,
    # that does not track average, but weightest (latest if tied) value,
    # and computes covariance matrix centered around that.
    # But perhaps the following method would work similarly well?
    def add_without_dominance_get_distance(self, vector_value, log_weight=0.0):
        """Update stats, avoid having the sample dominate, return old distance.

        If the weight of the incoming sample is far bigger
        than the weight of all the previous data together,
        convariance matrix would suffer from underflows.
        To avoid that, this method manipulates both weights
        before calling add().

        The old covariance matrix (before update) can define a metric.
        Shift is a vector, so the metric can be used to compute a distance
        between old average and new sample.

        :param vector_value: The value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type vector_value: iterable of float
        :type log_weight: float
        :returns: Updated self.
        :rtype: VectorStatTracker
        """
        lsw = self.log_sum_weight
        if lsw is not None and lsw < log_weight - 1.0:
            lsw = (lsw + log_weight) / 2.0
            log_weight = lsw
            self.log_sum_weight = lsw
        old_metric = copy.deepcopy(self.covariance_matrix)
        shift = self.add_get_shift(vector_value, log_weight)
        gradient = numpy.linalg.solve(old_metric, shift)
        distance = numpy.vdot(shift, gradient)
        return distance
