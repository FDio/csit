from abc import ABCMeta, abstractmethod


class Animal(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def make_sound(self):
        """Return sound string typical for this animal."""
        pass
