from collections import namedtuple


class TypeWrapper(object):
    def __init__(self, own_type):
        self.own_type = own_type

    @staticmethod
    def from_parameter(get_type, parameter):
        return TypeWrapper(get_type(parameter))


class ContainerTypeWrapper(TypeWrapper):
    def __init__(self, own_type, contained_types):
        super(ContainerTypeWrapper, self).__init__(own_type)
        self.contained_types = contained_types


