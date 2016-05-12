ducktest
========

Python source code may contain type hints in the form of docstrings or comments.
These are useful for the human reader as well as static code analysers.
ducktest is a command line tool to generate such type hints.

Python unit tests contain type information. Whether they contain complete type information seems to be a mere matter of
style. I consider it good practice to unit test code with the types (or corresponding mocks from mock.create_autospec)
that are actually used in production code.
Therefore, manually writing :type and :rtype tags into method docstrings seems to be a form of duplication.

ducktest remedies that situation by collecting type information from unit tests.
It executes unit tests and collects the types of *method parameters* and *return values* of
methods called in the process.
It also collects the spec classes of mock.Mock objects that are passed into or returned from methods.
Then ducktest writes that information into the :type and :rtype tags of the corresponding method docstrings.


installation
------------

install ducktest via pip: *pip install ducktest*


usage
-----

call ducktest from the command line: *python ducktest configuration_file*

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
top_level_dir           This is the first upward folder of your project, that is not a python package (relative to the
                        configuration_file). If the configuration_file resides in such a folder, this parameter should
                        be omitted. There must one or zero top_level_dir values in the configuration_file, not several.

execute_tests_in        Execute unit tests that reside in this folders.

write_to                Write type information to source code files residing in this folders.

exclude_parameter_names Do not write type information for parameters with these names. Currently used to exclude pretty
                        redundant information for self and cls parameters.

======================= ================================================================================================

ducktest deletes all previous :type and :rtype tags in edited docstrings
ducktest does not write tags for NoneType or a plain mock.Mock (without _spec_class)


known problems/bugs/TODOs
-------------------------

- Currently failing tests contribute type information, although it is potentially incorrect. Execute ducktest only
  while all tests pass.
- ducktest collects all types used in tests, even if they are sub- or supertypes of each other
- The types of objects in container types are not resolved yet.
- When a parameter is a class (not an instance), its type is *type* or *metaclass*. Calls to its classmethods will
  create warnings in static type checkers.
