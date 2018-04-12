# FIXME: License.

from AbstractRateProvider import AbstractRateProvider


class TimeTrackingRateProvider(AbstractRateProvider):
    """Delegating provider, tracks time spent by measurements."""

    def __init__(self, provider, overhead=0.5):
        """Inject provider to delegate to."""
        self.provider = provider
        self.overhead = overhead
        self.reset()

    def reset(self):
        """Start tracking anew."""
        self.total_time = 0.0
        """Seconds spent measuring since last zero."""
        self.measurements = 0

    def measure(self, duration, transmit_rate):
        """Track and delegate."""
        self.total_time += duration + self.overhead
        self.measurements += 1
        return self.provider.measure(duration, transmit_rate)
