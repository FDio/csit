
class AvgStdevMetadata(object):
    """Class for metadata specifying the average and standard deviation."""

    def __init__(self, size=0, avg=0.0, stdev=0.0):
        """Construct the metadata by setting the values needed.

        The values are sanitized, so faulty callers to not cause math errors.

        :param size: Number of values participating in this group.
        :param avg: Population average of the participating sample values.
        :param stdev: Population standard deviation of the sample values.
        :type size: int
        :type avg: float
        :type stdev: float
        """
        self.size = size if size >= 0 else 0
        self.avg = avg if size >= 1 else 0.0
        self.stdev = stdev if size >= 2 else 0.0

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return "size={size} avg={avg} stdev={stdev}".format(
            size=self.size, avg=self.avg, stdev=self.stdev)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return "AvgStdevMetadata(size={size},avg={avg},stdev={stdev})".format(
            size=self.size, avg=self.avg, stdev=self.stdev)
