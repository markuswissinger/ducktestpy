class AnotherClass(object):
    b = 1

    @classmethod
    def some_classmethod(cls, a):
        return a + cls.b