
Disclaimer: ducktest rewrites python source files. Being a work in progress it fails for certain reasons. Know how to
revert when ducktest breaks your code.


introduction
============

Python source code can be augmented by type hints.
These are useful for the human reader as well as static code analysers.
ducktest is a tool to generate type hints.

Unit tests should explain how to use your code. Good tests contain a lot of information about the types
used in your code. Tests written with ducktest in mind contain as much information as designated type hints.
Writing independent type hints is a form of duplication.

ducktest executes unit tests and collects the types of *method parameters* and *return values* of
methods called in the process. Then ducktest writes that information into the :type and :rtype tags of the
corresponding method docstrings.

Therefore ducktest creates a much closer link between your tests and your productive code. It will probably not catch
bugs that the tests you wrote to create the type hints will not catch. But it gives an incentive to write those tests
in the first place (and allows for autocompletion and navigation).

use cases
=========

minimal
-------

Consider some module::

    def do_something(a_parameter):
        return str(a_parameter)

and some test::

    class TestSome(unittest.TestCase):
        def test_do_something(self):
            assert do_something(1)=='1'

calling ducktest writes type information retrieved from the test into the docstring of the tested method::

    def do_something(a_parameter):
        """
        :type a_parameter: int
        :rtype: str
        """
        return str(a_parameter)


mocks
-----

Instances of mock.Mock with a *_spec* property trigger ducktest (such instances result e.g. from calls to
*mock.create_autospec*). The type of the *_spec* is written into the docstring.
Mocks with _spec=None are ignored.

Consider py.some_module::

    class SomeClass(object):
        pass

    def do_something(a_parameter):
        pass

and some test::

    class TestSome(unittest.TestCase):
        def test_do_something(self):
            some = mock.create_autospec(SomeClass)
            do_something(some)

calling ducktest writes type information retrieved from the test into the docstring of the tested method. For
non-builtin objects the full reference is written::

    class SomeClass(object):
        pass

    def do_something(a_parameter):
        """:type a_parameter: some.full.reference.SomeClass"""
        pass


Mocks are also the perfect opportunity to create type hints for abstract base classes.


iterable collections
--------------------

Consider some module::

    def get_first_element(a_parameter):
        return a_parameter[0]

and some test::

    class TestSome(unittest.TestCase):
        def test_get_first_element(self):
            assert get_first_element([1, 2, 3])==1

calling ducktest writes the type as well as contained types::

    def get_first_element(a_parameter):
        """
        :type a_parameter: list of int
        :rtype: int
        """
        return a_parameter[0]



dictionaries
------------

Consider some module::

    def get_value(a_parameter, key):
        return a_parameter[key]

and some test::

    class TestSome(unittest.TestCase):
        def test_get_value(self):
            assert get_value({1:'A', 2:'B', 3:'C'}, 2)=='B'

calling ducktest writes the type as well as contained types::

    def get_value(a_parameter):
        """
        :type a_parameter: dict of (int,str)
        :rtype: str
        """
        return a_parameter[key]


generators
----------

Consider some generator::

    def some_generator():
        yield 1

and some test::

    class TestSome(unittest.TestCase):
        def test_some_generator(self):
            for stuff in some_generator():
                assert stuff==1

Calling ducktest results in a generator rtype tag, the sphinx docstring format does not seem to define a *yield_type*
tag, so ducktest currently does not write one::

    def some_generator():
        """:rtype: generator"""
        yield 1


type hierarchies
----------------

If a type and its subtype both appear in the same :type or :rtype tag, the subtype is omitted from the tag. Types of
ojects in containers and mappings are considered. For example: if B is subtype of A, then list[B] is considered a
subtype of list[A].

installation
============

Install ducktest via pip::

    pip install ducktest


usage
=====

API
---

Create a python script on the top level of your project. For example run_ducktest.py::

    from ducktest.configuration import DucktestConfiguration

    DucktestConfiguration(__file__,
                          test_directories=[('demo', 'test'), ],
                          write_directories=['demo'],
                          ignore_call_parameter_names=('self', 'cls'),
                          ).run()

First parameter is always the calling file, that is used to determine the top level directory.
ducktest discovers and executes tests in test_directories, writes types in write_directories.
All directories are relative to the top level directory. So the script run_ducktest.py can be checked in to version
control. Directories with more than one level should be given as tuple, to avoid OS specific path separators.
Parameter names in ignore_call_parameter_names are ignored. The default should do.


pitfalls
========

settrace
--------

ducktest uses *sys.settrace*, therefore it can not be used on parts of your code that call *sys.settrace*
(and is itself not easily accessible by debuggers and such). It also can not evaluate python code that runs in
separate threads.

However, this is not a strong limitation since ducktest is supposed to execute unit tests. Unit tests really should not
call *sys.settrace* or do multi-threading.


limits of the sphinx notation
-----------------------------

-   classes as parameters can not be expressed
-   functions and methods as parameters can not be described well
-   Pycharm parses only tags that are on a single line, and therefore too long when multiple types are involved




notable (intended) behaviour
============================

-   ducktest uses the failfast option of unittest. ducktest does not write type information if any of the executed tests
    failed.

-   ducktest deletes *all* :type and :rtype tags in all files in the write_directories before writing. So a failed
    renaming does not result in a broken docstring. Type tags from other sources (e.g. the developer) will be lost.
    Just do never write those tags again by hand.

-   ducktest does not write tags for NoneType or a plain mock.Mock (without _spec_class)

-   empty container and mapping types are not printed, if there is a non-empty one: e.g. *list and list of int* is
    printed as *list of int*

TODO (unordered)
================

- how to handle @abstractmethod and @abstractproperty? Those functions are never executed (also not during tests) but
  deserve a type hint.
- introduce an *any* type...
- do not record types from tests that use *assertRaises*, since those might be wrong
- resolve old style classes
- When a parameter is a class (not an instance), its type is *type* or *metaclass*. Calls to its classmethods will
  create warnings in static type checkers. There seems to be no way to express this in the sphinx docstring
  format that is parsed by type checkers
- Useful unimplemented configuration options:
    - handle hand-written mocks
    - exclude subfolders from type writing
    - exclude subfolders from test execution
- write not only docstrings but python stubs as well
