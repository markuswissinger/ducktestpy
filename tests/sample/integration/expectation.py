def generator_example():
    """:rtype: generator"""
    yield 1


def non_builtin_example(a):
    """
    :type a: tests.sample.integration.stuff.Other or tests.sample.integration.stuff.Some
    :rtype: tests.sample.integration.stuff.Other or tests.sample.integration.stuff.Some
    """
    return a


def mock_example(a):
    """
    :type a: int or tests.sample.integration.stuff.Some
    :rtype: int or tests.sample.integration.stuff.Some
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


def with_any(any):
    """
    :type any: ducktest.ducktypes.Any
    :rtype: str
    """
    return 'any many mooh!'
