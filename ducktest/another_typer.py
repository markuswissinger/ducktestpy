import types
from abc import abstractmethod, ABCMeta
from collections import defaultdict, OrderedDict, Mapping, Container, Iterable

import mock
from future.utils import iteritems

CO_GENERATOR = 0x20
CO_VARARGS = 0x04
CO_KWARGS = 0x08


def has_varargs(frame):
    return frame.f_code.co_flags & CO_VARARGS != 0


def is_generator(frame):
    return frame.f_code.co_flags & CO_GENERATOR != 0


def get_first_line_number(frame):
    return frame.f_code.co_firstlineno


def get_function_name(frame):
    return frame.f_code.co_name


def get_file_name(frame):
    return frame.f_code.co_filename


def get_variable_names(frame):
    return frame.f_code.co_varnames


def get_local_variable(frame, variable_name):
    return frame.f_locals[variable_name]


def get_docstring(frame):
    try:
        return frame.f_code.co_consts[0]
    except IndexError:
        return None


class Processor(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.next_processor = None

    @abstractmethod
    def process(self, *args, **kwargs):
        pass


def last_after(processor):
    while processor.next_processor:
        processor = processor.next_processor
    return processor


def chain(*processors):
    for first, second in zip(processors[:-1], processors[1:]):
        last_after(first).next_processor = second
    return processors[0]


class DirectoriesValidater(Processor):
    def __init__(self, included_directories):
        super(DirectoriesValidater, self).__init__()
        self.included_directories = included_directories

    def process(self, frame, *args):
        for included_directory in self.included_directories:
            if get_file_name(frame).startswith(included_directory):
                self.next_processor.process(frame, *args)


class CallVariableSplitter(Processor):
    def process(self, frame):
        for name in get_variable_names(frame):
            try:
                value = get_local_variable(frame, name)
            except KeyError:
                continue
            self.next_processor.process(value, name, frame)


class ReturnVariableSplitter(Processor):
    def process(self, frame, return_value):
        self.next_processor.process(return_value, frame)


class NameValidater(Processor):
    def __init__(self, excluded_names):
        super(NameValidater, self).__init__()
        self.excluded_names = excluded_names

    def process(self, value, name, frame):
        if name not in self.excluded_names:
            self.next_processor.process(value, name, frame)


class TypeWrapper(object):
    def __init__(self, own_type):
        self.own_type = own_type

    @staticmethod
    def from_value(value):
        return TypeWrapper(type(value))


def get_plain_type(parameter):
    if isinstance(parameter, mock.Mock):
        if parameter._spec_class:
            return parameter._spec_class
        else:
            raise ValueError
    else:
        return type(parameter)


class MappingTypeWrapper(TypeWrapper):
    def __init__(self, own_type, mapped_types):
        super(MappingTypeWrapper, self).__init__(own_type)
        self.mapped_types = mapped_types

    @staticmethod
    def from_value(mapping):
        return MappingTypeWrapper(type(mapping), MappingTypeWrapper.mapped_types(mapping))

    @staticmethod
    def mapped_types(mapping):
        result = set()
        for key, value in iteritems(mapping):
            try:
                result.add((get_plain_type(key), get_plain_type(value)))
            except ValueError:
                pass
        return result


class ContainerTypeWrapper(TypeWrapper):
    def __init__(self, own_type, contained_types):
        super(ContainerTypeWrapper, self).__init__(own_type)
        self.contained_types = contained_types

    @staticmethod
    def from_value(container):
        return ContainerTypeWrapper(type(container), ContainerTypeWrapper.contained_types(container))

    @staticmethod
    def contained_types(container):
        result = set()
        for value in container:
            try:
                result.add(get_plain_type(value))
            except ValueError:
                pass
        return result


class GeneratorTypeProcessor(Processor):
    def __init__(self, return_types):
        super(GeneratorTypeProcessor, self).__init__()
        self.return_types = return_types

    def process(self, return_value, frame):
        if is_generator(frame):
            self.return_types.store(TypeWrapper(types.GeneratorType), frame)


class MockTypeProcessor(Processor):
    def __init__(self, call_types):
        super(MockTypeProcessor, self).__init__()
        self.call_types = call_types

    def process(self, value, *args):
        if isinstance(value, mock.Mock):
            if value._spec_class:
                self.call_types.store(TypeWrapper(value._spec_class), *args)
            else:
                return
        else:
            self.next_processor.process(value, *args)


class MappingTypeProcessor(Processor):
    def __init__(self, call_types):
        super(MappingTypeProcessor, self).__init__()
        self.call_types = call_types

    def process(self, value, *args):
        if isinstance(value, Mapping):
            self.call_types.store(MappingTypeWrapper.from_value(value), *args)
        else:
            self.next_processor.process(value, *args)


class ContainerTypeProcessor(Processor):
    def __init__(self, call_types):
        super(ContainerTypeProcessor, self).__init__()
        self.call_types = call_types

    def process(self, value, *args):
        if all([
            isinstance(value, Container),
            isinstance(value, Iterable),
            not isinstance(value, basestring),
            not isinstance(value, Mapping)
        ]):
            self.call_types.store(ContainerTypeWrapper.from_value(value), *args)
        else:
            self.next_processor.process(value, *args)


class PlainTypeProcessor(Processor):
    def __init__(self, type_repository):
        super(PlainTypeProcessor, self).__init__()
        self.type_repository = type_repository

    def process(self, value, *args):
        """implicit end of chain"""
        self.type_repository.store(TypeWrapper.from_value(value), *args)


class CallTypesRepository(object):
    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(lambda: (defaultdict(lambda: set()), [])))

    def store(self, a_type, name, frame):
        function_dict, parameter_order = self._dict[get_file_name(frame)][get_first_line_number(frame)]
        if name not in function_dict.keys():
            parameter_order.append(name)
        function_dict[name].add(a_type)

    def sorted_file_names(self):
        return sorted(self._dict.keys())

    @staticmethod
    def _sorted_per_line(function_dict, parameter_order):
        result = OrderedDict()
        for parameter_name in parameter_order:
            result[parameter_name] = function_dict[parameter_name]
        return result

    def sorted_call_types(self, file_name):
        findings_in_file = self._dict[file_name]
        line_numbers = sorted(findings_in_file.keys(), reverse=True)
        return [self._sorted_per_line(*findings_in_file[line_number]) for line_number in line_numbers]


class ReturnTypesRepository(object):
    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(set))

    def store(self, a_type, frame):
        self._dict[get_file_name(frame)][get_first_line_number(frame)].add(a_type)

    def sorted_file_names(self):
        return sorted(self._dict.keys())

    def sorted_return_types(self, file_name):
        findings_in_file = self._dict[file_name]
        line_numbers = sorted(findings_in_file.keys(), reverse=True)
        return [findings_in_file[line_number] for line_number in line_numbers]


class FrameProcessors(object):
    def __init__(self, configuration):
        """:type configuration: ducktest.config_reader.Configuration"""
        self.call_types = CallTypesRepository()
        self.return_types = ReturnTypesRepository()

        self.call_frame_processor = chain(
            DirectoriesValidater(configuration.write_docstrings_in_directories),
            CallVariableSplitter(),
            NameValidater(configuration.ignore_call_parameter_names),
            MockTypeProcessor(self.call_types),
            MappingTypeProcessor(self.call_types),
            ContainerTypeProcessor(self.call_types),
            PlainTypeProcessor(self.call_types),
        )

        self.return_frame_processor = chain(
            DirectoriesValidater(configuration.write_docstrings_in_directories),
            ReturnVariableSplitter(),
            MockTypeProcessor(self.return_types),
            MappingTypeProcessor(self.return_types),
            ContainerTypeProcessor(self.return_types),
            PlainTypeProcessor(self.return_types),
        )
