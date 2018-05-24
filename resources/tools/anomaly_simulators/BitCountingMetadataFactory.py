
import math

from BitCountingMetadata import BitCountingMetadata


class BitCountingMetadataFactory(object):
    """Class for factory which creates bit counting metadata from data."""

    @staticmethod
    def find_max_value(values):
        """Return the max value.

        This is a separate helper method,
        because the set of values is usually larger than in from_data().

        :param values: Run values to be processed.
        :type values: Iterable of float
        :returns: 0.0 or the biggest value found.
        :rtype: float
        """
        max_value = 0.0
        for value in values:
            if value > max_value:
                max_value = value
        return max_value

    def __init__(self, max_value):
        """Construct the factory instance with given max value.

        :param max_value: Maximal expected value.
        :type max_value: float
        """
        self.max_value = max_value

    def from_data(self, values):
        """Return new metadata object fitting the values.

        :param values: Run values to be processed.
        :type values: Iterable of float
        :returns: The metadata matching the values.
        :rtype: BitCountingMetadata
        """
        sum_0 = 0
        sum_1 = 0.0
        sum_2 = 0.0
        for value in values:
            sum_0 += 1
            sum_1 += value
            sum_2 += value * value
        if sum_0 < 1:
            return BitCountingMetadata(max_value=self.max_value)
        avg = sum_1 / sum_0
        stdev = math.sqrt(sum_2 / sum_0 - avg * avg)
        return BitCountingMetadata(
            max_value=self.max_value, size=sum_0, avg=avg, stdev=stdev)
