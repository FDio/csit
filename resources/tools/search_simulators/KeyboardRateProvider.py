# FIXME: License.

from AbstractRateProvider import AbstractRateProvider


class KeyboardRateProvider(AbstractRateProvider):
    """Report rate the user typed."""

    def get_drop_count(self, transmit_rate, duration):
        """Ask user for Dx."""
        print "Tr", transmit_rate
        print "d", duration
        print "0.5%", transmit_rate * duration / 200
        dx = input("Enter Dx:")
        return dx
