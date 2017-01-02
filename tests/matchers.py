from hamcrest.core.matcher import Matcher


class IsSameListOfLines(Matcher):
    def __init__(self, expected_items):
        self.expected_items = expected_items
        self.expected_item = None
        self.item = None

    def describe_to(self, description):
        pass

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.out = '\n'
        mismatch_description.append_text('Expected line {}: '.format(self.line))
        mismatch_description.append_description_of(self.expected_item)
        mismatch_description.append_text('\n but line {} was: '.format(self.line))
        mismatch_description.append_description_of(self.item)

    def matches(self, item, mismatch_description=None):
        match_result = self._matches(item)
        if not match_result and mismatch_description:
            self.describe_mismatch(item, mismatch_description)
        return match_result

    def _matches(self, items):
        i = 1
        for item, expected in zip(items, self.expected_items):
            i += 1
            if item != expected:
                self.item = item
                self.expected_item = expected
                self.line = i
                return False
        return True


def is_same_list_of_lines(expected):
    return IsSameListOfLines(expected)
