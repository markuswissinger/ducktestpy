from collections import OrderedDict
import types
import collections

import mock

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


class CallTypeWrapper(object):
    def __init__(self, frame):
        self.frame = frame

    @property
    def call_types(self):
        return OrderedDict()


def is_mapping_type(parameter):
    return isinstance(parameter, collections.MutableMapping)


def from_frame(frame, return_value):
    if is_generator(frame):
        return types.GeneratorType, set(), set()
    if isinstance(return_value, mock.Mock):
        return
    if is_mapping_type(return_value):
        return


class ReturnTypeWrapper(object):
    def __init__(self):
        self.own_type = None
        self.contained_types = set()
        self.mapped_types = set()

    def __eq__(self, other):
        return isinstance(other, ReturnTypeWrapper) \
               and self.own_type == other.own_type \
               and self.contained_types == other.contained_types \
               and self.mapped_types == other.mapped_types




class ReturnFrameWrapper(object):
    def __init__(self, frame, return_value):
        self.frame = frame
        self.return_value = return_value

    @property
    def path(self):
        return get_file_name(self.frame), get_first_line_number(self.frame)

    @staticmethod
    def _return_type(frame, return_value):
        if is_generator(frame):
            return set(types.GeneratorType)
        if is_mapping_type(return_value):

            return set()
