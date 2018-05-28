from abc import ABCMeta, abstractmethod


class AbstractGroupClassifier(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def classify(self, values):
        """Divide values into consecutive groups with metadata.

        The metadata does not need to follow any specific rules,
        although progression/regression/outlier description would be fine.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float
        :returns: Classified groups
        :rtype: Iterable of RunGroup
        """
        pass
