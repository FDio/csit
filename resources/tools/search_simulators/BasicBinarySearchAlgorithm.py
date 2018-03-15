# FIXME: License.

from AbstractSearchAlgorithm import AbstractSearchAlgorithm

class BasicBinarySearchAlgorithm(AbstractSearchAlgorithm):
    """Bisect using given number of iteration for both NDR and PDR.
    No fast fail, nor other smart stuff."""

    def __init__(self, rate_provider, iterations, duration):
        super(BasicBinarySearchAlgorithm, self).__init__(rate_provider)
        self.iterations = iterations
        self.duration = duration

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Proceed with iteration-aware method."""
        return self.ndrpdr(self.iterations, fail_rate, line_rate, allowed_drop_fraction)

    def ndrpdr(self, iterations, lower_bound, upper_bound, allowed_drop_fraction):
        """Bisect and determine which way to recurse."""
        if iterations < 1:
            return [lower_bound, upper_bound, lower_bound, upper_bound]
        tr = (lower_bound + upper_bound) / 2.0
        dr = self.rate_provider.get_drop_rate(tr, self.duration)
        fraction = dr / tr
        if fraction > allowed_drop_fraction:
            return self.ndrpdr(iterations - 1, lower_bound, tr, allowed_drop_fraction)
        if fraction <= 0:
            return self.ndrpdr(iterations - 1, tr, upper_bound, allowed_drop_fraction)
        pdr_lo, pdr_hi = self.pdr(iterations - 1, tr, upper_bound, allowed_drop_fraction)
        ndr_lo, ndr_hi = self.ndr(iterations - 1, lower_bound, tr)
        return [ndr_lo, ndr_hi, pdr_lo, pdr_hi]

    def pdr(self, iterations, lower_bound, upper_bound, allowed_drop_fraction):
        """Bisect and recurse for PDR."""
        if iterations < 1:
            return [lower_bound, upper_bound]
        tr = (lower_bound + upper_bound) / 2.0
        dr = self.rate_provider.get_drop_rate(tr, self.duration)
        fraction = dr / tr
        if fraction > allowed_drop_fraction:
            return self.pdr(iterations - 1, lower_bound, tr, allowed_drop_fraction)
        return self.pdr(iterations - 1, tr, upper_bound, allowed_drop_fraction)

    def ndr(self, iterations, lower_bound, upper_bound):
        """Bisect and recurse for NDR."""
        if iterations < 1:
            return [lower_bound, upper_bound]
        tr = (lower_bound + upper_bound) / 2.0
        dr = self.rate_provider.get_drop_rate(tr, self.duration)
        fraction = dr / tr
        if fraction > 0.0:
            return self.ndr(iterations - 1, lower_bound, tr)
        return self.ndr(iterations - 1, tr, upper_bound)
