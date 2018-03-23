# FIXME: License.

from abc import ABCMeta, abstractmethod


class AbstractSearchAlgorithm(object):
    """Abstract class with defining API for search algorithms."""

    __metaclass__ = ABCMeta

    def __init__(self, rate_provider):
        """Constructor, needs injected rate provider."""
        # TODO: Type check for AbstractRateProvider?
        self.rate_provider = rate_provider

    @abstractmethod
    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        # TODO: Should we require more arguments, related to precision or overall duration?
        """Return NdrPdrResult object with the narrowed measured data."""
        pass
