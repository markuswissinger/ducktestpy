A = ['A']
B = ['B']


def some():
    """
    :type full: list of str
    :type one: str
    :rtype: generator
    """
    full = A + B
    for one in full:
        yield one
