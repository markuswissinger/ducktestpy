A = ['A']
B = ['B']


def some():
    """:rtype: generator"""
    full = A + B
    for one in full:
        yield one
