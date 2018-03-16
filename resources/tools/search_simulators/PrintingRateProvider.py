# FIXME: License.

from AbstractRateProvider import AbstractRateProvider


class PrintingRateProvider(AbstractRateProvider):
    """Delegating provider, prints relevant values."""

    def __init__(self, provider):
        """Inject (non-printing) provider to delegate to."""
        self.provider = provider

    def measure(self, duration, transmit_rate):
        """Print and delegate."""
        print "Provider called with Tr", transmit_rate, "and d", duration
        measurement = self.provider.measure(duration, transmit_rate)
        print "Provider returned measurement:", repr(measurement)
        return measurement
