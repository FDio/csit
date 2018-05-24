from abc import ABCMeta, abstractmethod


class AbstractGroupMetadata(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        pass

    @abstractmethod
    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        pass
