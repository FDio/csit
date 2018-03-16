# FIXME: License.

from ReceiveRateMeasurement import ReceiveRateMeasurement


class ReceiveRateInterval(object):
    """Structure defining two Rr measurements, presumably close to each other."""

    def __init__(self, measured_low, measured_high):
        """Constructor, store the measurement after checking argument types."""
        # TODO: Type checking is not very pythonic, perhaps users can fix wrong usage without it?
        if not isinstance(measured_low, ReceiveRateMeasurement):
            raise TypeError("measured_low is not a ReceiveRateMeasurement: " + repr(measured_low))
        if not isinstance(measured_high, ReceiveRateMeasurement):
            raise TypeError("measured_high is not a ReceiveRateMeasurement: " + repr(measured_high))
        self.measured_low = measured_low
        self.measured_high = measured_high

    def __str__(self):
        """Return string as half-open interval."""
        return "[" + str(self.measured_low) + "," + str(self.measured_high) + ")"

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "ReceiveRateInterval(measured_low=" + repr(self.measured_low) + \
               ",measured_high=" + repr(self.measured_high) + ")"
