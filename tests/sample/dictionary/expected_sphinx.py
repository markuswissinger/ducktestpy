def some_kwargs(**kwargs):
    """
    :type kwargs: dict of (str,int)
    :rtype: dict of (str,int)
    some docstring
    """
    return kwargs


def another(*args, **kwargs):
    """
    :type args: tuple of int
    :type kwargs: c or d or i or t
    :rtype: tuple of int
    """
    return args


def yet_another(**kwargs):
    """:type kwargs: c or d or i or t"""
    pass


def some(a):
    """:type a: c or d or i or t"""
    pass
