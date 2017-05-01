A = ['A']
B = ['B']


def some():
    full = A + B
    for one in full:
        yield one


def another(b):
    full = A + B + b
    for one in full:
        yield one
