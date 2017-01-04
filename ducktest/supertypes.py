from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper, MappingTypeWrapper

is_subtype_functions = []


def is_subtype(a, b):
    """a is subtype of b"""
    return any((function(a, b) for function in is_subtype_functions))


def both_are_instances(a, b, wrapper_class):
    return isinstance(a, wrapper_class) and isinstance(b, wrapper_class)


def is_plain_subtype(a, b):
    return both_are_instances(a, b, PlainTypeWrapper) and issubclass(a.own_type, b.own_type)


def is_subtype_of_any(a, b_iterable):
    return any((is_subtype(a, b) for b in b_iterable))


def is_container_subtype(a, b):
    return both_are_instances(a, b, ContainerTypeWrapper) and issubclass(a.own_type, b.own_type) and \
           all((is_subtype_of_any(a_contained, b.contained_types) for a_contained in a.contained_types))


def keys(mapping_type_wrapper):
    return (mapped[0] for mapped in mapping_type_wrapper.mapped_types)


def values(mapping_type_wrapper):
    return (mapped[1] for mapped in mapping_type_wrapper.mapped_types)


def is_mapping_subtype(a, b):
    return both_are_instances(a, b, MappingTypeWrapper) and issubclass(a.own_type, b.own_type) \
           and all((is_subtype_of_any(a_key, keys(b)) for a_key in keys(a))) \
           and all((is_subtype_of_any(a_value, values(b)) for a_value in values(a)))


is_subtype_functions.extend([
    is_plain_subtype,
    is_container_subtype,
    is_mapping_subtype,
])


def remove_subtypes(some_types):
    result = set([])
    for a in some_types:
        should_add = True
        for b in some_types:
            if a is b:
                continue
            if is_subtype(a, b):
                should_add = False
        if should_add:
            result.add(a)
    return result
