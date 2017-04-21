def some_kwargs(**kwargs):
    """
    :type kwargs: dict of str,int
    :rtype: dict of str,int
    some docstring
    """
    return kwargs


def another(*args, **kwargs):
    """
    :type args: tuple of int
    :type kwargs: dict
    :rtype: tuple of int
    """
    return args


def yet_another(**kwargs):
    """:type kwargs: dict"""
    pass


def some(a):
    """:type a: dict"""
    pass
