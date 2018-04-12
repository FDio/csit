# FIXME: License.

from AbstractRateProvider import AbstractRateProvider
from ReceiveRateMeasurement import ReceiveRateMeasurement


class PromilesRateProvider(AbstractRateProvider):
    """Report Dx as configurable promile of Tx."""

    def __init__(self, promiles):
        """Constructor, stores promiles to use."""
        self.fraction = promiles / 1000.0

    def measure(self, duration, transmit_rate):
        """Compute Dx."""
        tx = int(duration * transmit_rate)
        return ReceiveRateMeasurement(duration, transmit_rate, tx, tx * self.fraction)
