import os


def _version():
    here = os.path.abspath(os.path.dirname(__file__))
    directory = os.path.dirname(here)
    with open(os.path.join(directory, 'ducktest', 'VERSION.txt')) as f:
        return f.read()


VERSION = _version()
