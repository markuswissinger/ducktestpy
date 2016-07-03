import abc
import collections
import types
from collections import OrderedDict

from future.utils import iteritems

CO_GENERATOR = 0x20


def is_generator(frame):
    return frame.f_code.co_flags & CO_GENERATOR != 0


def file_name(frame):
    return frame.f_code.co_filename


def first_line_number(frame):
    return frame.f_code.co_firstlineno


def get_docstring(frame):
    try:
        return frame.f_code.co_consts[0]
    except IndexError:
        return None


class Processor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.next_processor = None

    @abc.abstractmethod
    def process(self, *args, **kwargs):
        pass


class Terminator(Processor):
    def process(self, to_process):
        print('No processor for: {}'.format(to_process))


def last_processor_after(processor):
    while processor.next_processor:
        processor = processor.next_processor
    return processor


def chain(*processors):
    for first, second in zip(processors[:-1], processors[1:]):
        first.next_processor = last_processor_after(second)
    return processors[0]


def unchain(*processors):
    for processor in processors:
        processor.next_processor = None


class SimpleType(object):
    def __init__(self, simple_type):
        self.type = simple_type


class ReturnValueValidater(Processor):
    def process(self, frame, return_value):
        if return_value is None:
            return
        self.next_processor.process(frame, return_value)


class IncludedDirectoryValidater(Processor):
    def __init__(self, included_directories):
        super(IncludedDirectoryValidater, self).__init__()
        self.included_directories = included_directories

    def process(self, frame, *args):
        if self.__is_included(file_name(frame)):
            self.next_processor.process(frame, *args)

    def __is_included(self, file_name):
        for included_directory in self.included_directories:
            if file_name.startswith(included_directory):
                return True


class CallTypeFinder(Processor):
    def __init__(self, parameter_processor):
        super(CallTypeFinder, self).__init__()
        self.parameter_processor = parameter_processor

    def process(self, frame, *args):
        for name, value in self.call_parameters(frame):
            self.parameter_processor.process(name, value, frame)

    @staticmethod
    def call_parameters(frame):
        parameters = OrderedDict()
        for parameter_name in frame.f_code.co_varnames:
            try:
                parameters[parameter_name] = frame.f_locals[parameter_name]
            except(KeyError):
                pass
        return iteritems(parameters)


class NameValidater(Processor):
    def __init__(self, excluded_names):
        super(NameValidater, self).__init__()
        self.excluded_names = excluded_names

    def process(self, name, value, frame):
        if name in self.excluded_names:
            return
        self.next_processor.process(value, frame)


class MappingTypeStorer(Processor):
    def __init__(self, stored_types):
        super(MappingTypeStorer, self).__init__()
        self.stored_types = stored_types

    def process(self, parameter_value, frame):
        if isinstance(parameter_value, collections.Mapping):
            type_set = set()
            for key, value in iteritems(parameter_value):
                type_tuple = type(parameter_value), type(key), type(value)
                type_set.add(type_tuple)



class Setup(object):
    def __init__(self, conf):
        self.call_processor = chain(
            IncludedDirectoryValidater(conf.included_directories),
            CallTypeFinder(chain(
                NameValidater(conf.excluded_names),

            ))

        )
        self.return_processor = chain(
            ReturnValueValidater(),
            IncludedDirectoryValidater(conf.included_directories),

        )
