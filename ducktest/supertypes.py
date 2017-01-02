from ducktest.base import PlainTypeWrapper, ContainerTypeWrapper


def is_true_subclass_of(a, b):
    return issubclass(a, b) and not issubclass(b, a)


def is_plain_subtype(a, b):
    return isinstance(a, PlainTypeWrapper) and isinstance(b, PlainTypeWrapper) and is_true_subclass_of(a.own_type,
                                                                                                       b.own_type)


def is_container_subtype(a, b):
    return isinstance(a, ContainerTypeWrapper) and isinstance(b, ContainerTypeWrapper) and is_true_subclass_of(
        a.own_type, b.own_type)


def is_subtype_of(a, b):
    return is_plain_subtype(a, b)


def remove_subtypes(some_types):
    result = set([])
    for a in some_types:
        should_add = True
        for b in some_types:
            if is_subtype_of(a, b):
                should_add = False
        if should_add:
            result.add(a)
    return result
