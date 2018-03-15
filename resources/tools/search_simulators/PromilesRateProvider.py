# FIXME: License.

from AbstractRateProvider import AbstractRateProvider


class PromilesRateProvider(AbstractRateProvider):
    """Report Dx as configurable promile of Tx."""

    def __init__(self, promiles):
        """Constructor, stores promiles to use."""
        self.promiles = promiles

    def get_drop_count(self, transmit_rate, duration):
        """Compute Dx."""
        return transmit_rate * duration * self.promiles / 1000.0
