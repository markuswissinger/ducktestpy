import types
from collections import namedtuple, OrderedDict

from ducktest.another_typer import FunctionParameters, OrderedDefaultDict
from ducktest.type_wrappers import PlainTypeWrapper, ContainerTypeWrapper

SampleParameters = namedtuple('SampleParameters', ['call', 'ret'])

module_method = SampleParameters([
    FunctionParameters(1, OrderedDict([('a', {PlainTypeWrapper(type(1))})])),
], [
    FunctionParameters(1, {PlainTypeWrapper(type(1))}),
])

method_in_class = SampleParameters([
    FunctionParameters(5, OrderedDict([('a', {PlainTypeWrapper(type(1))})])),
    FunctionParameters(2, OrderedDict([('b', {PlainTypeWrapper(type(1))})])),
], [
    FunctionParameters(5, {PlainTypeWrapper(type(1))}),
    FunctionParameters(2, {PlainTypeWrapper(type(None))}),
])

generator = SampleParameters(
    [], [
        FunctionParameters(1, {PlainTypeWrapper(types.GeneratorType)})
    ]
)

classmethod = SampleParameters([
    FunctionParameters(4, OrderedDict([('a', {PlainTypeWrapper(type(1))})])),
], [
    FunctionParameters(4, {PlainTypeWrapper(type(1))}),
]
)

list = SampleParameters([
    FunctionParameters(line_number=1, types=OrderedDict([('a', {
        ContainerTypeWrapper(own_type=type([]), contained_types=frozenset([PlainTypeWrapper(own_type=type(1))])),
        ContainerTypeWrapper(own_type=type([]), contained_types=frozenset(
            [ContainerTypeWrapper(own_type=type([]), contained_types=frozenset([PlainTypeWrapper(own_type=type(1))])),
             PlainTypeWrapper(own_type=type(1)), PlainTypeWrapper(type(''))])),
        ContainerTypeWrapper(type([]), contained_types=frozenset([PlainTypeWrapper(type(''))]))})]))
], [
    FunctionParameters(line_number=1, types={
        ContainerTypeWrapper(own_type=type([]), contained_types=frozenset([PlainTypeWrapper(own_type=type(1))])),
        PlainTypeWrapper(own_type=type(1)),
        PlainTypeWrapper(own_type=type(''))})
]

)
