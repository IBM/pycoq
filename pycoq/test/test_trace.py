'''
sample test of pycoq.trace
'''


import logging
import os
import json
import pkg_resources

import numpy
import pytest

import pycoq.log
import pycoq.trace

import serlib.parser


def with_prefix(s: str) -> str:
    ''' adds package path as prefix '''
    return os.path.join(pkg_resources.resource_filename('pycoq', 'test'), s)

def aux_test_trace(name: str, write=False):
    lines = open(with_prefix(f"trace/{name}.in")).readlines()
    line = lines[0]
    parser = pycoq.trace.get_parser()
    record = pycoq.trace.parse_strace_line(parser, line)
    if write:
        json.dump(record, open(with_prefix(f"trace/{name}.out"), 'w'))
    else:
        assert record == json.load(open(with_prefix(f"trace/{name}.out")))

def test_trace1():
    aux_test_trace("t1")

