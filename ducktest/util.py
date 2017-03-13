import sys

DUCKTEST_TRACE_DISPATCH = None


def setup_ducktest():
    if DUCKTEST_TRACE_DISPATCH:
        sys.settrace(DUCKTEST_TRACE_DISPATCH)


def teardown_ducktest():
    if DUCKTEST_TRACE_DISPATCH:
        sys.settrace(None)
