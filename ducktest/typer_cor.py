import abc
import types
from collections import OrderedDict

CO_GENERATOR = 0x20


def is_generator(frame):
    return frame.f_code.co_flags & CO_GENERATOR != 0


def get_file_name(frame):
    return frame.f_code.co_filename


def get_first_line_number(frame):
    return frame.f_code.co_firstlineno


def get_docstring(frame):
    try:
        return frame.f_code.co_consts[0]
    except IndexError:
        return None


def call_parameters(frame):
    parameters = OrderedDict()
    for parameter_name in frame.f_code.co_varnames:
        try:
            parameters[parameter_name] = frame.f_locals[parameter_name]
        except(KeyError):
            pass
    return parameters


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

    def process(self, frame_wrapper):
        if self.__is_included(frame_wrapper.file_name):
            self.next_processor.process(frame_wrapper)

    def __is_included(self, file_name):
        for included_directory in self.included_directories:
            if file_name.startswith(included_directory):
                return True


class Setup(object):
    def __init__(self):
        self.call_processor = chain(

        )
        self.return_processor = chain(

        )
