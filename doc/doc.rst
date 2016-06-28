========
ducktest
========

Disclaimer: ducktest rewrites python source files. It fails for certain reasons_. Know how to revert when ducktest
breaks your code.


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
        type a_parameter: int
        rtype: str
        """
        return str(a_parameter)


mocks
-----

Instances of mock.Mock with a _spec property (such instances result e.g. from calls to mock.create_autospec) trigger
ducktest. Therefore the type of the _spec is written into the docstring.
Mocks without _spec are ignored.

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
        type a_parameter: py.SomeClass
        """
        pass


installation
============

Install ducktest via pip::

    pip install ducktest


usage
=====

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



Behaviours / TODO
=================

notable intended behaviour
--------------------------

- ducktest deletes all previous :type and :rtype tags in edited docstrings
- ducktest does not write tags for NoneType or a plain mock.Mock (without _spec_class)

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
    - delete all :type and :rtype tags from written files (not just the overwritten ones)
- write not only docstrings but python stubs as well