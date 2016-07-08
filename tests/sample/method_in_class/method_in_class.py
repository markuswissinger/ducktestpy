class SomeClass(object):
    def __init__(self, b):
        self.b = b

    def some_method(self, a):
        A = (1, 2)
        B, C = A
        return self.b + a
