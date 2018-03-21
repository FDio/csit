# FIXME: License.

from AbstractSearchAlgorithm import AbstractSearchAlgorithm
from ReceiveRateMeasurement import ReceiveRateMeasurement
from ReceiveRateInterval import ReceiveRateInterval
from NdrPdrResult import NdrPdrResult

class BasicBinarySearchAlgorithm(AbstractSearchAlgorithm):
    """Bisect using given number of iteration for both NDR and PDR.
    No fast fail, nor other smart stuff."""

    def __init__(self, rate_provider, iterations, duration):
        super(BasicBinarySearchAlgorithm, self).__init__(rate_provider)
        self.iterations = iterations
        self.duration = duration

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform boundary measurements, proceed with iteration-aware method."""
        line_measurement = self.rate_provider.measure(self.duration, line_rate)
        if line_measurement.drop_count <= 0:
            line_interval = ReceiveRateInterval(line_measurement, line_measurement)
            return NdrPdrResult(line_interval, line_interval)
        fail_measurement = self.rate_provider.measure(self.duration, fail_rate)
        if fail_measurement.drop_rate > fail_rate * allowed_drop_fraction:
            fail_interval = ReceiveRateInterval(fail_measurement, fail_measurement)
            return NdrPdrResult(fail_interval, fail_interval)
        return self.ndrpdr(self.iterations, fail_measurement, line_measurement, allowed_drop_fraction)

    def ndrpdr(self, iterations, lower_measurement, upper_measurement, allowed_drop_fraction):
        """Bisect and determine which way to recurse."""
        if iterations < 1:
            common_interval = ReceiveRateInterval(lower_measurement, upper_measurement)
            return NdrPdrResult(common_interval, common_interval)
        middle_transmit_rate = (lower_measurement.transmit_rate + upper_measurement.transmit_rate) / 2
        middle_measurement = self.rate_provider.measure(self.duration, middle_transmit_rate)
        fraction = middle_measurement.drop_rate / middle_transmit_rate
        if fraction > allowed_drop_fraction:
            return self.ndrpdr(iterations - 1, lower_measurement, middle_measurement, allowed_drop_fraction)
        if fraction <= 0:
            return self.ndrpdr(iterations - 1, middle_measurement, upper_measurement, allowed_drop_fraction)
        ndr_interval = self.ndr(iterations - 1, lower_measurement, middle_measurement)
        pdr_interval = self.pdr(iterations - 1, middle_measurement, upper_measurement, allowed_drop_fraction)
        return NdrPdrResult(ndr_interval, pdr_interval)

    def pdr(self, iterations, lower_measurement, upper_measurement, allowed_drop_fraction):
        """Bisect and recurse for PDR."""
        if iterations < 1:
            return ReceiveRateInterval(lower_measurement, upper_measurement)
        middle_transmit_rate = (lower_measurement.transmit_rate + upper_measurement.transmit_rate) / 2
        middle_measurement = self.rate_provider.measure(self.duration, middle_transmit_rate)
        fraction = middle_measurement.drop_rate / middle_transmit_rate
        if fraction > allowed_drop_fraction:
            return self.pdr(iterations - 1, lower_measurement, middle_measurement, allowed_drop_fraction)
        return self.pdr(iterations - 1, middle_measurement, upper_measurement, allowed_drop_fraction)

    def ndr(self, iterations, lower_measurement, upper_measurement):
        """Bisect and recurse for NDR."""
        if iterations < 1:
            return ReceiveRateInterval(lower_measurement, upper_measurement)
        middle_transmit_rate = (lower_measurement.transmit_rate + upper_measurement.transmit_rate) / 2
        middle_measurement = self.rate_provider.measure(self.duration, middle_transmit_rate)
        fraction = middle_measurement.drop_rate / middle_transmit_rate
        if fraction > 0.0:
            return self.ndr(iterations - 1, lower_measurement, middle_measurement)
        return self.ndr(iterations - 1, middle_measurement, upper_measurement)
