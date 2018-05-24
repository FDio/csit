
import math

from BitCountingMetadata import BitCountingMetadata


class ClassifiedBitCountingMetadata(BitCountingMetadata):
    """Class for metadata which includes classification."""

    def __init__(self, max_value, size=0, avg=0.0, stdev=0.0
                 classification=None):
        """Delegate to ancestor constructors and set classification.

        :param max_value: Maximal expected value.
        :param size: Number of values participating in this group.
        :param avg: Population average of the participating sample values.
        :param stdev: Population standard deviation of the sample values.
        :param classification: Arbitrary object classifying this group.
        :type max_value: float
        :type size: int
        :type avg: float
        :type stdev: float
        :type classification: object
        """
        super(ClassifiedBitCountingMetadata, self).__init__(
            max_value, size, avg, stdev)
        self.classification = classification

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        super_str = str(super(ClassifiedBitCountingMetadata, self))
        return super_str + " classification={classification}".format(
            classification=self.classification)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return ("AvgStdevMetadata(max_value={max_value},size={size}," +
                "avg={avg},stdev={stdev},classification={cls})").format(
                    max_value=self.max_value, size=self.size,
                    avg=self.avg, stdev=self.stdev, cls=self.classification)
