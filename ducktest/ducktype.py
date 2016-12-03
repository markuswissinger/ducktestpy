from mock import Mock


class Any(Mock):
    """
    Mock has any method and property.
    Any is intended to replace all other types of a tag when present,
    effectively acting as superclass of any other type.
    """
    pass
