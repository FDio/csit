from abc import ABCMeta, abstractmethod


class AbstractRunsProvider(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_runs(self, max_runs):
        """Perform runs, return their results and descriptions.

        The number of runs can be lower than the maximum,
        typically when the provider uses historic data.

        The descriptions are there mainly for specific providers
        which create values with progressions and regressions,
        the grouping and metadata is there to compare with classifier output.

        :param max_runs: Upper limit to the number of runs to perform.
        :type max_runs: int
        :returns: Run values, grouped with metadata.
        :rtype: Iterable of RunGroup
        """
        pass
