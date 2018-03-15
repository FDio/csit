# FIXME: License.

from random import randint

from AbstractRateProvider import AbstractRateProvider


class RandomRateProvider(AbstractRateProvider):
    """Random Dx generator. 50-50 for Dx=0, uniform drop fraction otherwise."""

    def get_drop_count(self, transmit_rate, duration):
        """Generate Dx."""
        if randint(0, 1):
            return 0
        tx = transmit_rate * duration
        return randint(0, int(tx))
