A = ['A']
B = ['B']


def some():
    """:rtype: generator"""
    full = A + B
    for one in full:
        yield one


def another(b):
    """
    :type b: list of str
    :rtype: generator
    """
    full = A + B + b
    for one in full:
        yield one
