========
ducktest
========

Disclaimer: ducktest rewrites python source files. It fails for certain reasons_. Know how to revert when ducktest
breaks your code.

installation
============

Install ducktest via pip::

    pip install ducktest


usage
=====

configuration file
------------------

Call ducktest from the comand line on a configuration file::

    ducktest cofiguration_file.cfg

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
top_level_dir           This is the first upward folder of your project relative to the
                        configuration_file, that is not a python package (aka has no __init__.py).
                        If the configuration_file resides in such a folder, this parameter should
                        be omitted. There must be one or zero top_level_dir values in the configuration_file, not
                        several. The top_level_dir is used by the unittest.TestLoader.discover method.

execute_tests_in        Execute unit tests that reside in this folders.

write_to                Write type information to source code files residing in this folders.

exclude_parameter_names Do not write type information for parameters with these names. Currently used to exclude pretty
                        redundant information for self and cls parameters.

======================= ================================================================================================



use case
========

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

