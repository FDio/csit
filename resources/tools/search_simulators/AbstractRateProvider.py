# FIXME: License.

from abc import ABCMeta, abstractmethod


class AbstractRateProvider(object):
    """Abstract class defining API for rate providers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_drop_count(self, transmit_rate, duration):
        """Return Dx. Do not print nor log the value, leave that to callers."""
        return 0.0

    def get_drop_rate(self, transmit_rate, duration):
        """Get Dx, return computed Dr."""
        return self.get_drop_count(transmit_rate, duration) / float(duration)
