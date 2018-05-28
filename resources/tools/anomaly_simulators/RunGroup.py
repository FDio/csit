
class RunGroup(object):

    def __init__(self, metadata, values):
        """Create the group from metadata and values.

        :param metadata: Metadata object to associate with the group.
        :param values: The runs belonging to this group.
        :type metadata: AbstractGroupMetadata
        :type values: Iterable of float or od AvgStdevMetadata
        """
        self.metadata = metadata
        self.values = values
