# FIXME: License.

from AbstractRateProvider import AbstractRateProvider
from ReceiveRateMeasurement import ReceiveRateMeasurement

class KeyboardRateProvider(AbstractRateProvider):
    """Report rate the user typed."""

    def measure(self, duration, transmit_rate):
        """Print context and ask user for Dx."""
        tx = int(duration * transmit_rate)
        print "Tr", transmit_rate
        print "Tx", tx
        print "d", duration
        print "0.5%", tx / 200.0
        dx = input("Enter Dx:")
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
