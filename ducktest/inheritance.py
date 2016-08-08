from ducktest.type_wrappers import PlainTypeWrapper, ContainerTypeWrapper


def combinations(some_set):
    a_copy = set(some_set)
    for some in a_copy:
        other_set = set(a_copy)
        other_set.remove(some)
        for other in other_set:
            yield some, other


def handle_plain(wrappers):
    own_types = {wrapper.own_type for wrapper in wrappers if type(wrapper) == PlainTypeWrapper}
    for some, other in combinations(own_types):
        if issubclass(some, other):
            own_types.remove(some)
    return {PlainTypeWrapper(filtered) for filtered in own_types}


def handle_container(wrappers):
    for some, other in combinations(wrappers):
        if issubclass(some.own_type, other.own_type):
            wrappers.remove(some)
            wrappers.add(ContainerTypeWrapper(other, some.contained_types))

