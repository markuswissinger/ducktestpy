import abc

import mock


class Any(mock.Mock):
    """
    This type has any method and property and is superclass to all types.
    Is intended to replace all other types in a tag (when ducktest omits subtypes of a type within a given tag)
    """
    __metaclass__ = abc.ABCMeta

    @classmethod
    def __subclasshook__(cls, other_class):
        return True
