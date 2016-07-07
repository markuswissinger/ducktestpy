from collections import defaultdict
import sys


def A(a):
    return a


def B(b):
    return A(b)


def C(c):
    return B(c)


def defaultdict_of_finding():
    return defaultdict(Finding)


class Tracer(object):
    def runcall(self, method, *args, **kwargs):
        sys.settrace(self.trace_dispatch)
        method(*args, **kwargs)

    def trace_dispatch(self, frame, event, arg):
        if event == 'call':
            self.on_call(frame)
            return self.trace_dispatch
        elif event == 'return':
            self.on_return(frame, arg)

    def on_call(self, frame):
        # print 'called: {}'.format(frame.f_code.co_name)
        pass

    def on_return(self, frame, return_value):
        # print 'returned: {}'.format(frame.f_code.co_name)
        pass

    def __init__(self, frame_factory):
        self.frame_factory = frame_factory
        self.findings = defaultdict(defaultdict_of_finding)

    def user_call(self, frame, argument_list):
        wrapped_frame = self.frame_factory.create(frame)
        if wrapped_frame.must_be_stored and wrapped_frame.call_types:
            self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_call(wrapped_frame)

    def user_return(self, frame, return_value):
        wrapped_frame = self.frame_factory.create(frame, return_value=return_value)
        if wrapped_frame.must_be_stored and wrapped_frame.return_type:
            self.findings[wrapped_frame.file_name][wrapped_frame.first_line_number].add_return(wrapped_frame)

    def all_file_names(self):
        return sorted(self.findings.keys())

    def get_sorted_findings(self, file_name):
        return sorted(self.findings[file_name].values(), reverse=True)


if __name__ == '__main__':
    tracer = Tracer()
    tracer.runcall(C, 1)
