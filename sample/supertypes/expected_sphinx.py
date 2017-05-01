class A(object):
    pass


class B(A):
    pass


def some(a):
    """
    :type a: sample.supertypes.original.A
    :rtype: list of sample.supertypes.original.A
    """
    return [a]


def another(a):
    """
    :type a: dict of sample.supertypes.original.A,int
    :rtype: dict of sample.supertypes.original.A,int
    """
    return a


def yet_another(a):
    """
    :type a: dict of int,sample.supertypes.original.A
    :rtype: dict of int,sample.supertypes.original.A
    """
    return a


def empty(a):
    """
    :type a: dict of sample.supertypes.original.A,int
    :rtype: dict of sample.supertypes.original.A,int
    """
    return a
