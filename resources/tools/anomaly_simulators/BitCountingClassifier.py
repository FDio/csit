
from BitCountingGroup import BitCountingGroup
from BitCountingGroupList import BitCountingGroupList
from BitCountingMetadataFactory import BitCountingMetadataFactory
from ClassifiedMetadataFactory import ClassifiedMetadataFactory


class BitCountingClassifier(object):

    def classify(self, values):
        """Return the values in groups of optimal bit count.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: Classified group list.
        :rtype: list of BitCountingGroup
        """
        max_value = BitCountingMetadataFactory.find_max_value(values)
        factory = BitCountingMetadataFactory(max_value)
        opened_at = []
        closed_before = [BitCountingGroupList()]
        for index, value in enumerate(values):
            singleton = BitCountingGroup(factory, [value])
            newly_opened = closed_before[index].with_group_appended(singleton)
            opened_at.append(newly_opened)
            record_group_list = newly_opened
            for previous in range(index):
                previous_opened_list = opened_at[previous]
                still_opened = (
                    previous_opened_list.with_value_added_to_last_group(value))
                opened_at[previous] = still_opened
                if still_opened.bits < record_group_list.bits:
                    record_group_list = still_opened
            closed_before.append(record_group_list)
        partition = closed_before[-1]
        average = None
        for group in partition:
            if average is None:
                average = group.metadata.avg
            if group.metadata.avg == average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "normal")
            elif group.metadata.avg < average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "regression")
            elif group.metadata.avg > average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "progression")
        return partition
