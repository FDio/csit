
import random

from AbstractRunsProvider import AbstractRunsProvider
from AvgStdevMetadataFactory import AvgStdevMetadataFactory
from BitCountingMetadataFactory import BitCountingMetadataFactory
from RunGroup import RunGroup


class ZeroGressionProvider(AbstractRunsProvider):
    """Provider class for data with a zero gressions.

    A "gression" is the union of regression and progression.
    The data consists of two groups.
    Each group consists of random data following a Gauss distribution,
    but with the same pair of mu and sigma.
    As the data is random, the actual average and variance can be different.
    The metadata contains the actual average and stdev (instad of mu and sigma).
    """

    def __init__(self, max_mu, max_sigma):
        """Construct provider, limited by arguments.

        :param max_mu: Maximal value for mu parameter.
            The actual mu is chosen uniformly between zero and this.
        :param max_sigma: Maximal value for sigma parameter.
            The actual sigma is chosen uniformly between zero and this.
        :type max_mu: float
        :type max_sigma: float
        """
        self.max_mu = max_mu
        self.max_sigma = max_sigma

    def get_runs(
            self, max_runs, min_streak, seed=0, samples=1, pseudosamples=1):
        """Decide group parameters, generate data, return that.

        The number of runs belonging to the first group is chosen uniformly
        between min_streak and and max_runs - min_streak.
        Single common sigma is chosen uniformly from zero to max_sigma.
        Single common mu is chosen independently uniformly, from zero to max_mu.

        :param max_runs: Number of runs to perform.
        :param min_streak: Minimal number of runs in a group.
        :type max_runs: int
        :type min_streak: int
        :returns: Run values, grouped with metadata.
        :rtype: Iterable of RunGroup
        """
        random.seed(seed)
        first_size = random.randint(min_streak, max_runs - min_streak)
        second_size = max_runs - first_size
        sigma = random.uniform(0.0, self.max_sigma)
        mu = random.uniform(0.0, self.max_mu)
        first_values = []
        second_values = []
        for i in range(first_size):
            for j in range(samples):
                values = []
                for k in range(pseudosamples):
                    values.append(random.gauss(mu, sigma))
                metadata = AvgStdevMetadataFactory.from_data(values)
                metadata.size = 1
                metadata.stdev = 0.0
                first_values.append(metadata)
        for i in range(second_size):
            for j in range(samples):
                values = []
                for k in range(pseudosamples):
                    values.append(random.gauss(mu, sigma))
                metadata = AvgStdevMetadataFactory.from_data(values)
                metadata.size = 1
                metadata.stdev = 0.0
                second_values.append(metadata)
        all_values = list(first_values)
        all_values.extend(second_values)
        max_value = BitCountingMetadataFactory.find_max_value(all_values)
        factory = BitCountingMetadataFactory(max_value)
        first_metadata = factory.from_data(first_values)
        second_metadata = factory.from_data(second_values)
        first_group = RunGroup(first_metadata, first_values)
        second_group = RunGroup(second_metadata, second_values)
        return first_group, second_group
