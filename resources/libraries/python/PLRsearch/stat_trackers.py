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

# TODO: The preferred way to consume this code is via a pip package.
# If your project copies code instead, make sure your pylint check does not
# require these imports to be absolute and descending from your superpackage.
from log_plus import log_plus


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
        the tracker state is invalid.  Use reset method
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

    def reset(self):
        """Set state to empty data of proper dimensionality."""
        self.averages = [0.0 for first in range(self.dimension)]
        # TODO: Examine whether we can gain speed by tracking triangle only.
        self.covariance_matrix = [[0.0 for second in range(self.dimension)]
                                  for first in range(self.dimension)]
        # TODO: In Python3, list comprehensions are generators,
        # so they are not indexable. Put list() when converting.

    def add(vector_value, log_weight=0.0):
        """Update stats corresponding to addition of another sample.

        :param vector_value: The value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type vector_value: iterable of float
        :type log_weight: float
        """
        dimension = self.dimension
        old_log_sum_weight = self.log_sum_weight
        if old_log_sum_weight is None:
            # First sample.
            self.log_sum_weight = log_weight
            self.averages = [vector_value[index] for index in range(dimension)]
            return
        old_averages = self.averages
        covariance_matrix = self.covariance_matrix
        new_log_sum_weight = log_plus(old_log_sum_weight, log_weight)
        data_ratio = math.exp(old_log_sum_weight - new_log_sum_weight)
        sample_ratio = math.exp(log_weight - new_log_sum_weight)
        shift = [vector_value[index] - old_averages[index]
                 for index in range(dimension)]
        # TODO: Consider returning shift.
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
        self.average = new_average
        # self.covariance_matrix still points to the object we updated in-place.

# TODO: There are some uses for such a vector tracker,
# that does not track average, but weightest (latest if tied) value,
# and computes covariance matrix centered around that.
# But perhaps the average-tracking one works similarly well?


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

    def copy(self):
        """Return new ScalarStatTracker instance with the same state as self.

        The point of this method is the return type, instances of subclasses
        can get rid of their additional data this way.

        :returns: New instance with the same core state.
        :rtype: ScalarStatTracker
        """
        return ScalarStatTracker(
            self.log_sum_weight, self.average, self.log_variance)

    def add(scalar_value, log_weight=0.0):
        """Update stats corresponding to addition of another sample.

        :param scalar_value: The scalar value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type scalar_value: float
        :type log_weight: float
        """
        old_log_sum_weight = self.log_sum_weight
        if old_log_sum_weight is None:
            # First sample.
            self.log_sum_weight = log_weight
            self.average = scalar_value
            return
        old_average = self.average
        log_variance = self.log_variance
        new_log_sum_weight = log_plus(old_log_sum_weight, log_weight)
        log_sample_ratio = log_weight - new_log_sum_weight
        sample_ratio = math.exp(log_sample_ratio)
        shift = scalar_value - old_average
        new average = old_average + shift * sample_ratio
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
        super(ScalarDualStatTracker, self).__init__(
            log_sum_weight, average, log_variance)
        self.secondary = ScalarStatTracker(
            log_sum_secondary_weight, secondary_average, log_secondary_variance)
        self.max_log_weight = max_log_weight

    def add(scalar_value, log_weight=0.0):
        """Update both stats corresponding to addition of another sample.

        :param scalar_value: The scalar value of the sample.
        :param log_weight: Natural logarithm of weight of the sample.
            Default: 0.0 (as log of 1.0).
        :type scalar_value: float
        :type log_weight: float
        """
        primary = super(ScalarDualStatTracker, self)
        if self.max_log_weight is not None and log_weight < self.max_log_weight:
            self.secondary.add(scalar_value, log_weight)
            primary.add(scalar_value, log_weight)
            return
        self.max_log_weight = log_weight
        self.secondary = primary.copy()
        primary.add(scalar_value, log_weight)
