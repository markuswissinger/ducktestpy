"""
Copyright 2016 Markus Wissinger. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


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


def key_sets(mapping_type_wrapper):
    return (mapped[0] for mapped in mapping_type_wrapper.mapped_types)


def value_sets(mapping_type_wrapper):
    return (mapped[1] for mapped in mapping_type_wrapper.mapped_types)


def each_is_subtype_of_some_in(key_set_a, key_set_b):
    return all((is_subtype_of_any(a_key, key_set_b) for a_key in key_set_a))


def all_compatible(a_sets, b_sets):
    return_value = True
    for a_set in a_sets:
        return_value = False
        for b_set in b_sets:
            if not each_is_subtype_of_some_in(a_set, b_set):
                return False
            return_value = True
    return return_value


def is_mapping_subtype(a, b):
    return both_are_instances(a, b, MappingTypeWrapper) \
           and issubclass(a.own_type, b.own_type) \
           and all_compatible(key_sets(a), key_sets(b)) \
           and all_compatible(value_sets(a), value_sets(b))


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
