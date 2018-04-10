# FIXME: License.

from random import randint

from AbstractRateProvider import AbstractRateProvider
from ReceiveRateMeasurement import ReceiveRateMeasurement


class RandomRateProvider(AbstractRateProvider):
    """Random Dx generator. 50-50 for Dx=0, uniform drop fraction otherwise."""

    def measure(self, duration, transmit_rate):
        """Random generate Dx."""
        tx = duration * transmit_rate
        dx = 0
        if randint(0, 1):
            dx = randint(0, int(tx))
        return ReceiveRateMeasurement(duration, transmit_rate, tx, dx)
