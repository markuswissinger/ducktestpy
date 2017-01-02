from abc import abstractmethod

from ducktest.base import chain, Processor, PlainTypeWrapper


def is_true_subclass_of(a, b):
    return issubclass(a, b) and not issubclass(b, a)


class TypeFilter(Processor):
    wrapper = None

    def process(self, a, b):
        if type(a) == self.wrapper and type(b) == self.wrapper:
            return self._process(a, b)
        else:
            return self.next_processor.process(a, b)

    @abstractmethod
    def _process(self, a, b):
        pass


class PlainTypeFilter(TypeFilter):
    wrapper = PlainTypeWrapper

    def _process(self, a, b):
        return not is_true_subclass_of(a.own_type, b.own_type)


class PassFilter(Processor):
    def process(self, *args, **kwargs):
        return True


filter_processor = chain(
    PlainTypeFilter(),
    PassFilter(),
)


def remove_subtypes(some_types):
    result = set([])
    for a in some_types:
        should_add = True
        for b in some_types:
            if not filter_processor.process(a, b):
                should_add = False
        if should_add:
            result.add(a)
    return result
