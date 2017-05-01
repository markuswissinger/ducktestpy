def generator_example():
    """:rtype: generator"""
    yield 1


def non_builtin_example(a):
    """
    :type a: sample.integration.stuff.Other or sample.integration.stuff.Some
    :rtype: sample.integration.stuff.Other or sample.integration.stuff.Some
    """
    return a


def mock_example(a):
    """
    :type a: int or sample.integration.stuff.Some
    :rtype: int or sample.integration.stuff.Some
    """
    return a


def list_example(a):
    """
    :type a: list of int or list of str
    :rtype: list of int or list of str
    """
    return a


def multi_line_docstring_example():
    """
    :rtype: str
    La \ndi dee
    One
    Two
    Three
    """
    return 'Eric the half a bee'


def two_line_docstring():
    """
    :rtype: int
    a b c d e f g
    Eric the half a bee
    """
    return 1


def single_line_return_value(a):
    return 1


def single_line_docstring(a):
    """
    :type a: str
    :rtype: str
    One line
    """
    return a


def single_result_line():
    """:rtype: int"""
    return 1


def new_docstring(a):
    """
    :type a: str
    :rtype: str
    """
    return a


def no_docstring():
    return None
