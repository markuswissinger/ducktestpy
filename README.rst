ducktest
========

Python source code can have type hints.
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
