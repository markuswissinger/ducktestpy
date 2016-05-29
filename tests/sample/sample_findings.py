import types

from ducktest.typer import Finding, TypeWrapper
from tests.sample.autospec.autospec import SomeClassToAutospec
from tests.sample.imported_types.to_import import ToImportA, ToImportB


def module_method(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_method'
    finding.variable_names = ('a',)
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper(1)}})
    finding.return_types.update({TypeWrapper(1)})
    finding.docstring = None
    return [finding]


def method_in_class(full_file):
    finding_5 = Finding()
    finding_5.file_name = full_file
    finding_5.function_name = 'some_method'
    finding_5.variable_names = ('a',)
    finding_5.first_line_number = 5
    finding_5.call_types.update({'a': {TypeWrapper(1)}})
    finding_5.return_types.update({TypeWrapper(1)})
    finding_5.docstring = None

    finding_2 = Finding()
    finding_2.file_name = full_file
    finding_2.function_name = '__init__'
    finding_2.variable_names = ('b',)
    finding_2.first_line_number = 2
    finding_2.call_types.update({'b': {TypeWrapper(1)}})
    finding_2.docstring = None

    return [finding_5, finding_2]


def generator(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_generator'
    finding.variable_names = tuple()
    finding.first_line_number = 1
    finding.return_types.add(TypeWrapper(None, generator=True))
    finding.docstring = None
    return [finding]


def class_method(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_classmethod'
    finding.variable_names = ('a',)
    finding.first_line_number = 4
    finding.call_types['a'] = {TypeWrapper(1)}
    finding.return_types = {TypeWrapper(2)}
    finding.docstring = None
    return [finding]


def single_type_list(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'get_first_item'
    finding.variable_names = ('a',)
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper([1])}})
    finding.return_types.update({TypeWrapper(1)})
    finding.docstring = None
    return [finding]


def imported_types(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'use_imported_types'
    finding.variable_names = ('a', 'b')
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper(ToImportA())}})
    finding.call_types.update({'b': {TypeWrapper(ToImportB())}})
    finding.return_types.update({TypeWrapper('')})
    finding.docstring = None
    return [finding]


def several_calls(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'call_me_several_times'
    finding.variable_names = ('a',)
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper(1)}})
    finding.return_types.update({TypeWrapper(1)})
    finding.docstring = None
    return [finding]


def autospec_call(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'use_autospec'
    finding.variable_names = ('a',)
    finding.first_line_number = 4
    finding.call_types.update({'a': {TypeWrapper(SomeClassToAutospec())}})
    finding.return_types.update({TypeWrapper('')})
    finding.docstring = 'use some auto spec, not.'
    return [finding]


def plain_mock(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_method'
    finding.variable_names = ('a',)
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper(1)}})
    finding.return_types.update({TypeWrapper(1)})
    finding.docstring = None
    return [finding]
