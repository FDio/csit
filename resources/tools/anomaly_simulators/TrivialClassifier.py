
from AvgStdevMetadata import AvgStdevMetadata
from RunGroup import RunGroup


class TrivialClassifier(object):

    def classify(self, values):
        """Return the values in single group with AvgStdevMetadata.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float
        :returns: Classified group
        :rtype: Singleton list of RunGroup
        """
        return [RunGroup(AvgStdevMetadata(values), values)]
