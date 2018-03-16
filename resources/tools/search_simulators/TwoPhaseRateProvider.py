# FIXME: License.

from random import uniform

from AbstractRateProvider import AbstractRateProvider
from ReceiveRateMeasurement import ReceiveRateMeasurement


class TwoPhaseRateProvider(AbstractRateProvider):
    """Report Dx as sum of two phases, each uniformly random Rr.
    Rr does NOT increase with Tr nor decrease with duration."""

    def __init__(self, first_phase_duration=0.002, first_rr_lo=3333333.0,
                 first_rr_hi=4000000.0, second_rr_lo=4150000.0, second_rr_hi=4200000.0):
        """Constructor, stores parameters to use."""
        self.first_phase_duration = first_phase_duration
        self.first_rr_lo = first_rr_lo
        self.first_rr_hi = first_rr_hi
        self.second_rr_lo = second_rr_lo
        self.second_rr_hi = second_rr_hi

    def measure(self, duration, transmit_rate):
        """Compute Dx according to two phase model."""
        first_phase_duration = min(duration, self.first_phase_duration)
        first_phase_tx = int(first_phase_duration * transmit_rate)
        first_phase_rr = uniform(self.first_rr_lo, self.first_rr_hi)
        first_phase_rx = int(first_phase_duration * first_phase_rr)
        first_phase_dx = max(0, first_phase_tx - first_phase_rx)
        if first_phase_duration >= duration:
            return ReceiveRateMeasurement(first_phase_duration, first_phase_tx, first_phase_dx)
        second_phase_duration = duration - first_phase_duration
        second_phase_tx = int(second_phase_duration * transmit_rate)
        second_phase_rr = uniform(self.second_rr_lo, self.second_rr_hi)
        second_phase_rx = int(second_phase_duration * second_phase_rr)
        second_phase_dx = max(0, second_phase_tx - second_phase_rx)
        return ReceiveRateMeasurement(first_phase_duration + second_phase_duration,
                                      first_phase_tx + second_phase_tx,
                                      first_phase_dx + second_phase_dx)
