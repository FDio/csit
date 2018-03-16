# FIXME: License.

from AbstractRateProvider import AbstractRateProvider


class PrintingRateProvider(AbstractRateProvider):
    """Delegating provider, prints relevant values.
    Printing is against API, but this is simpler than adding printing to algorithms."""

    def __init__(self, provider):
        """Inject (non-printing) provider to delegate to."""
        self.provider = provider

    def get_drop_count(self, transmit_rate, duration):
        """Print and delegate."""
        print "Provider called with Tr", transmit_rate, "and d", duration
        dx = self.provider.get_drop_count(transmit_rate, duration)
        print "Provider returned Dx", dx
        return dx
