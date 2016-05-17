import types

from ducktest.typer import Finding, TypeWrapper


def module_method(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_method'
    finding.first_line_number = 1
    finding.call_types.update({'a': {TypeWrapper(1)}})
    finding.return_types.update({TypeWrapper(1)})
    finding.docstring = None
    return [finding]


def method_in_class(full_file):
    finding_5 = Finding()
    finding_5.file_name = full_file
    finding_5.function_name = 'some_method'
    finding_5.first_line_number = 5
    finding_5.call_types.update({'a': {TypeWrapper(1)}})
    finding_5.return_types.update({TypeWrapper(1)})
    finding_5.docstring = None

    finding_2 = Finding()
    finding_2.file_name = full_file
    finding_2.function_name = '__init__'
    finding_2.first_line_number = 2
    finding_2.call_types.update({'b': {TypeWrapper(1)}})
    finding_2.docstring = None

    return [finding_5, finding_2]


def generator(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_generator'
    finding.first_line_number = 1
    finding.return_types.add(TypeWrapper(None, generator=True))
    finding.docstring = None
    return [finding]


def class_method(full_file):
    finding = Finding()
    finding.file_name = full_file
    finding.function_name = 'some_classmethod'
    finding.first_line_number = 4
    finding.call_types['a'] = {TypeWrapper(1)}
    finding.return_types = {TypeWrapper(2)}
    finding.docstring = None
    return [finding]
