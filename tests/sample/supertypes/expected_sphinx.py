class A(object):
    pass


class B(A):
    pass


def some(a):
    """
    :type a: tests.sample.supertypes.original.A
    :rtype: tests.sample.supertypes.original.A
    """
    return a