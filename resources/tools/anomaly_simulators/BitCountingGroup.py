
from RunGroup import RunGroup


class BitCountingGroup(RunGroup):

    def __init__(self, metadata_factory, values=[]):
        """Create the group from metadata factory and values.

        :param metadata_factory: Factory object to create metadata with.
        :param values: The runs belonging to this group.
        :type metadata_factory: BitCountingMetadataFactory
        :type values: Iterable of float or od AvgStdevMetadata
        """
        self.metadata_factory = metadata_factory
        metadata = metadata_factory.from_data(values)
        super(BitCountingGroup, self).__init__(metadata, values)

    def with_run_added(self, value):
        """Create and return a new group with one more run that self.

        :param value: The run value to add to the group.
        :type value: float or od AvgStdevMetadata
        :returns: New group with the run added.
        :rtype: BitCountingGroup
        """
        values = list(self.values)
        values.append(value)
        return BitCountingGroup(self.metadata_factory, values)
        # TODO: Is there a good way to save some computation
        # by copy&updating the metadata incrementally?
