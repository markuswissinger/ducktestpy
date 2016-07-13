from collections import namedtuple, OrderedDict

from ducktest.another_typer import FunctionParameters
from ducktest.type_wrappers import PlainTypeWrapper

SampleParameters = namedtuple('SampleParameters', ['call', 'ret'])

module_method = SampleParameters([FunctionParameters(1, OrderedDict([('a', {PlainTypeWrapper(type(1))})])), ],
                                 [FunctionParameters(1, {PlainTypeWrapper(type(1))}), ])
