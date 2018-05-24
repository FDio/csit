
import math


class AvgStdevMetadata(object):
    """Class for metadata specifying the average and standard deviation."""

    def __init__(self, values):
        """Construct the metadata by examining the runs' values.

        :param values: The run values to process.
        :type values: Iterable of float
        """
        sum_0 = 0
        sum_1 = 0.0
        sum_2 = 0.0
        for value in values:
            sum_0 += 1
            sum_1 += value
            sum_2 += value * value
        if sum_0 < 1:
            self.runs = 0
            self.avg = 0.0
            self.stdev = 0.0
            return
        avg = sum_1 / sum_0
        stdev = math.sqrt(sum_2 / sum_0 - avg * avg)
        self.runs = sum_0
        self.avg = avg
        self.stdev = stdev

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return "n={n} avg={avg} stdev={stdev}".format(
            n=self.runs, avg=self.avg, stdev=self.stdev)

    def __repr__(self):
        """Return string executable as Python constructor call.

        Note that because Python does not support multiple constructors,
        and we have opted for the constructor which computes from data,
        the returned value is not a valid statement.

        TODO: Is it worth having direct constructor and .fromdata() factory?

        :returns: Executable constructor call.
        :rtype: str
        """
        return "AvgStdevMetadata(runs={runs},avg={avg},stdev={stdev})".format(
            runs=self.runs, avg=self.avg, stdev=self.stdev)
