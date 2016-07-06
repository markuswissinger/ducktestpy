========
ducktest
========

Disclaimer: ducktest rewrites python source files. Being a work in progress it fails for certain reasons. Know how to
revert when ducktest breaks your code.


introduction
============

Python source code can be augmented by type hints.
These are useful for the human reader as well as static code analysers.
ducktest is a command line tool to generate such type hints.

Python unit tests contain type information. Whether they contain complete type information seems to be a mere matter of
style. I consider it good practice to unit test code with the types (or corresponding mocks from mock.create_autospec)
that are actually used in production code.
Therefore, manually writing :type and :rtype tags into method docstrings seems to be a form of duplication.

ducktest solves that problem by collecting type information from unit tests.
It executes unit tests and collects the types of *method parameters* and *return values* of
methods called in the process.
It also collects the spec classes of mock.Mock objects that are passed into or returned from methods.
Then ducktest writes that information into the :type and :rtype tags of the corresponding method docstrings.


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
        """
        :type a_parameter: some.full.reference.SomeClass
        """
        pass


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


installation
============

Install ducktest via pip::

    pip install ducktest


usage
=====

First run your tests - then run ducktest - then run your tests again.
First test run is necessary because ducktests does not yet check if your tests pass.
Last test run is useful since ducktest still might break something.


configuration file
------------------

Call ducktest from the comand line on a configuration file::

    ducktest ducktest.cfg

The configuration_file is assumed to be on the top level of your project folder.
All given paths in that file are relative to its location. It is good practice to keep the
configuration_file in your version control system (e.g. git), so that all contributors can use the same configuration.
Slash and backslash both work as path separators, to reduce cross-platform problems between linux or windows users.
A # symbol marks the rest of the line as comment.

The file is organized in whitespace separated lines: *parameter_name* *value1* *value2*
All given parameters are added to lists, so::

    a_parameter value1 value2

is equivalent to::

    a_paramter value1
    a_paramter value2


An example configuration file::

    # top_level_dir         py/
    execute_tests_in        py/demo/
    write_to                py/demo/
    exclude_parameter_names self cls

======================= ================================================================================================
parameter               description
======================= ================================================================================================
top_level_dir           This is the first upward folder of your project that is not a python package
                        (a.k.a. has no __init__.py). Give the path relative to the
                        configuration_file.
                        If the configuration_file resides in such a folder, this parameter should
                        be omitted. There must be one or zero top_level_dir values in the configuration_file, not
                        several. The top_level_dir is used by the unittest.TestLoader.discover method.

execute_tests_in        Execute all unit tests that reside in this folders.

write_to                Write type information to source code files residing in this folders.

exclude_parameter_names Do not write type information for parameters with these names. Currently used to exclude pretty
                        redundant information for self and cls parameters.

======================= ================================================================================================


pitfalls
========

newline in docstring
--------------------

An unescaped newline in a docstring will break the code after a ducktest run. So **always** escape::

    \n -> \\n
    \r -> \\r

etc.


Behaviours / TODO
=================

notable (intended) behaviour
----------------------------

-   ducktest deletes *all* :type and :rtype tags in docstrings it touches before writing. So a failed renaming does not
    result in a broken docstring. Type tags from other sources (e.g. the developer) will be lost. Just do never write
    those tags again by hand.

-   ducktest does not write tags for NoneType or a plain mock.Mock (without _spec_class)

TODO
----

- Old style classes are not resolved yet
- ducktest collects all types used in tests, even if they are sub- or supertypes of each other
- Currently failing tests contribute type information, although it is potentially incorrect. Execute ducktest only
  while all tests pass.
- When a parameter is a class (not an instance), its type is *type* or *metaclass*. Calls to its classmethods will
  create warnings in static type checkers. There seems to be no way to express this correctly in the sphinx docstring
  format
- Useful but missing configuration options:
    - handle hand-written mocks
    - exclude subfolders from type writing
    - exclude subfolders from test execution
    - optionally delete all :type and :rtype tags from written files (not just the overwritten ones)
- write not only docstrings but python stubs as well