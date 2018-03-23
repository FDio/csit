# FIXME: License.

import logging

from AbstractRateProvider import AbstractRateProvider


class LoggingRateProvider(AbstractRateProvider):
    """Delegating provider, logs relevant values at info level."""

    def __init__(self, provider):
        """Inject (non-printing) provider to delegate to."""
        self.provider = provider

    def measure(self, duration, transmit_rate):
        """Print and delegate."""
        logging.info("Provider called with Tr %s and d %s", transmit_rate, duration)
        measurement = self.provider.measure(duration, transmit_rate)
        logging.info("Provider returned measurement: %s", measurement)
        return measurement
