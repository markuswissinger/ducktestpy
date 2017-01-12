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

from abc import abstractmethod, ABCMeta
from collections import namedtuple


class Processor(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.next_processor = None

    @abstractmethod
    def process(self, *args, **kwargs):
        pass


class ChainTerminator(Processor):
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


PlainTypeWrapper = namedtuple('PlainTypeWrapper', 'own_type')
ContainerTypeWrapper = namedtuple('ContainerTypeWrapper', ['own_type', 'contained_types'])
MappingTypeWrapper = namedtuple('MappingTypeWrapper', ['own_type', 'mapped_types'])
