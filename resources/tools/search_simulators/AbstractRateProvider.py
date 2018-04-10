# FIXME: License.

from abc import ABCMeta, abstractmethod


class AbstractRateProvider(object):
    """Abstract class defining API for rate providers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def measure(self, duration, transmit_rate):
        """Return ReceiveRateMeasurement object with the measurement result."""
        pass
