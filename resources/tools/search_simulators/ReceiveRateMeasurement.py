# FIXME: License.

class ReceiveRateMeasurement(object):
    """Structure defining the result of single Rr measurement."""

    def __init__(self, duration, target_tr, transmit_count, drop_count):
        """Constructor, normalize primary and compute secondary quantities."""
        self.duration = float(duration)
        self.target_tr = float(target_tr)
        self.transmit_count = int(transmit_count)
        self.drop_count = int(drop_count)
        self.receive_count = transmit_count - drop_count
        self.transmit_rate = transmit_count / self.duration
        self.drop_rate = drop_count / self.duration
        self.receive_rate = self.receive_count / self.duration
        self.drop_fraction = self.drop_rate / self.transmit_rate
        # TODO: Do we want to store also the real time (duration + overhead)?

    def __str__(self):
        """Return string reporting Rr."""
        return "d=" + str(self.duration) + ",Tr=" + str(self.target_tr) + ",Df=" + str(self.drop_fraction)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "ReceiveRateMeasurement(duration=" + repr(self.duration) + \
               ",target_tr=" + repr(self.target_tr) + \
               ",transmit_count=" + repr(self.transmit_count) + \
               ",drop_count=" + repr(self.drop_count) + ")"
