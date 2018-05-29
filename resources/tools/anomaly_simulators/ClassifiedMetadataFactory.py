
import math

from ClassifiedBitCountingMetadata import ClassifiedBitCountingMetadata


class ClassifiedMetadataFactory(object):
    """Class for factory which adds classification to bit counting metadata."""

    @staticmethod
    def add_classification(metadata, classification):
        """Return new metadata object with added classification.

        TODO: Is there a way to add classification to any metadata,
        without messing up constructors and __repr__()?

        FIXME: Factories take raw resources. Find a name for the thing
        which takes semi-finished products. Transformer?

        :param metadata: Existing metadata without classification.
        :param classification: Arbitrary object classifying this group.
        :type metadata: BitCountingMetadata
        :type classification: object
        :returns: The metadata with added classification.
        :rtype: ClassifiedBitCountingMetadata
        """
        return ClassifiedBitCountingMetadata(
            max_value=metadata.max_value, size=metadata.size, avg=metadata.avg,
            stdev=metadata.stdev, classification=classification)
