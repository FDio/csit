
from BitCountingMetadataFactory import BitCountingMetadataFactory
from RunGroup import RunGroup


class TrivialClassifier(object):

    def classify(self, values):
        """Return the values in single group with bits counted.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float
        :returns: Classified group
        :rtype: Singleton list of RunGroup with BitCountingMetadata.
        """
        max_value = BitCountingMetadataFactory.find_max_value(values)
        factory = BitCountingMetadataFactory(max_value)
        metadata = factory.from_data(values)
        return [RunGroup(metadata, values)]
