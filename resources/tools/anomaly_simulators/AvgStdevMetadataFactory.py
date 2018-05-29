
import math

from AvgStdevMetadata import AvgStdevMetadata


class AvgStdevMetadataFactory(object):
    """Class factory which creates avg,stdev metadata from data."""

    @staticmethod
    def from_data(values):
        """Return new metadata object fitting the values.

        :param values: Run values to be processed.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: The metadata matching the values.
        :rtype: AvgStdevMetadata
        """
        sum_0 = 0
        sum_1 = 0.0
        sum_2 = 0.0
        for value in values:
            if isinstance(value, AvgStdevMetadata):
                sum_0 += value.size
                sum_1 += value.avg * value.size
                sum_2 += value.stdev * value.stdev * value.size
                sum_2 += value.avg * value.avg * value.size
            else:  # The value is assumed to be float.
                sum_0 += 1
                sum_1 += value
                sum_2 += value * value
        if sum_0 < 1:
            return AvgStdevMetadata()
        avg = sum_1 / sum_0
        stdev = math.sqrt(sum_2 / sum_0 - avg * avg)
        ret_obj = AvgStdevMetadata(size=sum_0, avg=avg, stdev=stdev)
#        print repr(values)
#        print repr(ret_obj)
        return ret_obj
