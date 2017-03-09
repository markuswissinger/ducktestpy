A = ['A']
B = ['B']


def some():
    full = A + B
    for one in full:
        yield one
