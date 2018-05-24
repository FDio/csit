
import random

from AbstractRunsProvider import AbstractRunsProvider
from AvgStdevMetadata import AvgStdevMetadata
from RunGroup import RunGroup


class SingleGressionProvider(AbstractRunsProvider):
    """Provider class for data with a single gression.

    A "gression" is the union of regression and progression.
    The data consists of two groups.
    Each group consists of random data following a Gauss distribution,
    but with different mu and sigma.
    As the data is random, the actual average and variance can be different.
    The metadata contains the actual average and stdev (instad of mu and sigma).
    """

    def __init__(self, max_mu, max_sigma, max_shift):
        """Construct provider, limited by arguments.

        :param max_mu: Maximal value for mu parameter.
            The actual mu is chosen uniformly between zero and this.
        :param max_sigma: Maximal value for sigma parameter.
            The actual sigma is chosen uniformly between zero and this.
        :param max_shift: The difference between the two group's mu values
            will be less than this multiplied by the first group's sigma.
        :type max_mu: float
        :type max_sigma: float
        :type max_shift: float
        """
        self.max_mu = max_mu
        self.max_sigma = max_sigma
        self.max_shift = max_shift

    def get_runs(self, max_runs):
        """Decide group parameters, generate data, return that.

        The number of runs belonging to the first group is chosen uniformly
        between zero and max_runs.
        Both sigmas are chosen independently uniformly from zero to max_sigma.
        Both mus are chosen independently uniformly, from zero to max_mu.
        While the mus violate max_shift, both mus are chosen again.

        :param max_runs: Number of runs to perform.
        :type max_runs: int
        :returns: Run values, grouped with metadata.
        :rtype: Iterable of RunGroup
        """
        first_size = random.randint(0, max_runs)
        second_size = max_runs - first_size
        first_sigma = random.uniform(0.0, self.max_sigma)
        second_sigma = random.uniform(0.0, self.max_sigma)
        while 1:
            first_mu = random.uniform(0.0, self.max_mu)
            second_mu = random.uniform(0.0, self.max_mu)
            if abs(first_mu - second_mu) < first_sigma * self.max_shift:
                break
        first_values = []
        second_values = []
        for _ in range(first_size):
            first_values.append(random.gauss(first_mu, first_sigma))
        for _ in range(second_size):
            second_values.append(random.gauss(second_mu, second_sigma))
        first_metadata = AvgStdevMetadata(first_values)
        second_metadata = AvgStdevMetadata(second_values)
        first_group = RunGroup(first_metadata, first_values)
        second_group = RunGroup(second_metadata, second_values)
        return first_group, second_group
