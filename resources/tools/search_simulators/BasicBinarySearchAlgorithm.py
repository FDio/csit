# FIXME: License.

from AbstractSearchAlgorithm import AbstractSearchAlgorithm
from ReceiveRateMeasurement import ReceiveRateMeasurement
from ReceiveRateInterval import ReceiveRateInterval
from NdrPdrResult import NdrPdrResult

class BasicBinarySearchAlgorithm(AbstractSearchAlgorithm):
    """Bisect using given number of iteration for both NDR and PDR.
    No fast fail, nor other smart stuff."""

    def __init__(self, rate_provider, duration, width):
        super(BasicBinarySearchAlgorithm, self).__init__(rate_provider)
        self.width = width
        self.duration = duration

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform boundary measurements, proceed with iteration-aware method."""
        line_measurement = self.rate_provider.measure(self.duration, line_rate)
        #if line_measurement.drop_count <= 0:
        #    line_interval = ReceiveRateInterval(line_measurement, line_measurement)
        #    return NdrPdrResult(line_interval, line_interval)
        fail_measurement = self.rate_provider.measure(self.duration, fail_rate)
        #if fail_measurement.drop_rate > fail_rate * allowed_drop_fraction:
        #    fail_interval = ReceiveRateInterval(fail_measurement, fail_measurement)
        #    return NdrPdrResult(fail_interval, fail_interval)
        ndr = self.bisect(fail_measurement, line_measurement, 0.0)
        pdr = self.bisect(fail_measurement, line_measurement, allowed_drop_fraction)
        return NdrPdrResult(ndr, pdr)

    def bisect(self, lower_measurement, upper_measurement, allowed_drop_fraction):
        """Bisect and recurse for PDR of given Df."""
        if upper_measurement.target_tr - lower_measurement.target_tr < self.width:
            return ReceiveRateInterval(lower_measurement, upper_measurement)
        middle_target_tr = (lower_measurement.target_tr + upper_measurement.target_tr) / 2.0
        middle_measurement = self.rate_provider.measure(self.duration, middle_target_tr)
        if middle_measurement.drop_fraction > allowed_drop_fraction:
            return self.bisect(lower_measurement, middle_measurement, allowed_drop_fraction)
        return self.bisect(middle_measurement, upper_measurement, allowed_drop_fraction)
