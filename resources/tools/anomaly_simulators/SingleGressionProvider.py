
import random

from AbstractRunsProvider import AbstractRunsProvider
from AvgStdevMetadataFactory import AvgStdevMetadataFactory
from BitCountingMetadataFactory import BitCountingMetadataFactory
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

    def __init__(self, max_mu, max_sigma, max_shift, min_shift):
        """Construct provider, limited by arguments.

        :param max_mu: Maximal value for mu parameter.
            The actual mu is chosen uniformly between zero and this.
        :param max_sigma: Maximal value for sigma parameter.
            The actual sigma is chosen uniformly between zero and this.
        :param max_shift: The difference between the two group's mu values
            will be less than this multiplied by the sigma.
        :param min_shift: The difference between the two group's mu values
            will be more than this multiplied by the sigma.
        :type max_mu: float
        :type max_sigma: float
        :type max_shift: float
        :type min_shift: float
        """
        self.max_mu = max_mu
        self.max_sigma = max_sigma
        self.max_shift = max_shift
        self.min_shift = min_shift

    def get_runs(
            self, max_runs, min_streak, seed=0, samples=1, pseudosamples=1,
            iron_out=True):
        """Decide group parameters, generate data, return that.

        The number of runs belonging to the first group is chosen uniformly
        between min_streak and and max_runs-min_streak.
        Single common sigma is chosen uniformly from zero to max_sigma.
        Both mus are chosen independently uniformly, from zero to max_mu.
        While the mus violate max_shift, both mus are chosen again.

        :param max_runs: Number of runs to perform.
        :param min_streak: Minimal number of runs in a group.
        :param seed: Random seed to initialize with.
        :param samples: Number of values one run produces.
        :param subsamples: Numer of values internally generated for one sample.
        :param iron_out: If true, sample is considered to be a single trial.
        :type max_runs: int
        :type min_streak: int
        :type seed: long
        :type samples: int
        :type subsamples: int
        :type iron_out: boolean
        :returns: Run values, grouped with metadata.
        :rtype: Iterable of RunGroup
        """
        random.seed(seed)
        while 1:
            first_size = random.randint(min_streak, max_runs - min_streak)
            second_size = max_runs - first_size
            sigma = random.uniform(0.0, self.max_sigma)
            first_mu = random.uniform(0.0, self.max_mu)
            second_mu = random.uniform(0.0, self.max_mu)
            abs_shift = abs(first_mu - second_mu)
            if abs_shift >= sigma * self.max_shift:
                continue
            if abs_shift <= sigma * self.min_shift:
                continue
            print "sigma", sigma, "shift", second_mu - first_mu
            break
        first_values = []
        second_values = []
        for i in range(first_size):
            for j in range(samples):
                values = []
                for k in range(pseudosamples):
                    values.append(random.gauss(first_mu, sigma))
                metadata = AvgStdevMetadataFactory.from_data(values)
                if iron_out:
                    metadata.size = 1
                    metadata.stdev = 0.0
                first_values.append(metadata)
        for i in range(second_size):
            for j in range(samples):
                values = []
                for k in range(pseudosamples):
                    values.append(random.gauss(second_mu, sigma))
                metadata = AvgStdevMetadataFactory.from_data(values)
                if iron_out:
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
