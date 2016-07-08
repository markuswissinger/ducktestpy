ducktest
========

Python source code can be augmented by type hints.
These are useful for the human reader as well as static code analysers.
ducktest is a command line tool to generate type hints.

Since Python is a dynamically typed language, its source code is quite immune to static code analysers.
Python programs are best analysed at runtime.

Unit tests are meant to explain how your code should be used. At runtime, good tests contain all
(or at least most of the) information about the types used in your code. Manually writing type hints is a form of
duplication.

So, it seems quite natural to examine the unit tests at runtime, extract type information and use it for type hints.
ducktest does exactly that. It executes unit tests and collects the types of *method parameters* and *return values* of
methods called in the process. Then ducktest writes that information into the :type and :rtype tags of the
corresponding method docstrings.
