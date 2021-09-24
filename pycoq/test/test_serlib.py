'''
sample test of pycoq.serlib
'''


import logging
import os
import json
import pkg_resources

import numpy
import pytest

import pycoq.log


import serlib.parser


def with_prefix(s: str) -> str:
    ''' adds package path as prefix '''
    return os.path.join(pkg_resources.resource_filename('pycoq', 'test'), s)


def test_hash_bytestring0():
    ''' tests serlib.hash bytestring function len 0 '''
    assert serlib.parser.hash_bytestring(b'') == 5371

def test_hash_bytestring1():
    ''' tests serlib.hash bytestring function len 1 '''
    assert serlib.parser.hash_bytestring(b'\0') == 257*5371

def test_hash_bytestring2():
    ''' tests serlib.hash bytestring function len 2 '''
    assert serlib.parser.hash_bytestring(b'\0\0') == 257*257*5371

def test_hash_bytestring4():
    ''' tests serlib.hash bytestring function len 4 '''
    assert serlib.parser.hash_bytestring(b'test') == 23432804277179



def test_sexpparser_parse_string0():
    ''' tests parsing single bytestring into postfix '''
    parser = serlib.parser.SExpParser()
    res = parser.postfix_of_sexp('((a b c)d(a b c)(e f) g)')
    ans = numpy.array([1,2,3,-3,4,1,2,3,-3,5,6,-2,7,-5],
                      dtype=numpy.intc)
    assert all(res == ans)



def test_sexpparser_parse_string1():
    ''' tests parsing two sequential bytestrings into postfix '''
    parser = serlib.parser.SExpParser()
    res0 = parser.postfix_of_sexp('((a b c)d(a b c)(e f) g)')
    ans0 = numpy.array([1,2,3,-3,4,1,2,3,-3,5,6,-2,7,-5],
                      dtype=numpy.intc)
    ans0_ann = serlib.cparser.annotate(ans0)
    res0_ann = numpy.array([0,  1,  2,  0,  4,  5,  6,  7,  5,  9, 10,  9, 12,  0], dtype=numpy.intc)

    assert all(res0 == ans0)
    #assert all(ans0_ann == res0_ann)

def test_sexpparser_parse_string2():
    parser = serlib.parser.SExpParser()
    res0 = parser.postfix_of_sexp('((a b c)d(a b c)(e f) g)')
    ans0 = numpy.array([1,2,3,-3,4,1,2,3,-3,5,6,-2,7,-5],
                      dtype=numpy.intc)

    res1 = parser.postfix_of_sexp('(g g a b Ф)')
    ans1 = numpy.array([7,7,1,2,8,-5], dtype=numpy.intc)

    res2 = parser.dict
    ans_string2 = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'Ф': 8}
    ans2 = {key.encode('utf8'): value for key, value in ans_string2.items()}

    assert all(res1 == ans1)
    #assert res2 == ans2


def aux_serlib_parse_bytestring_new(s, address):
    sparser = serlib.parser.SExpParser()
    res0a = sparser.postfix_of_bytestring(s, address)
    res0b = sparser.parse_bytestring_new(s, address)
    pycoq.log.info(f"test {res0a} == {res0b}")
    assert all(res0a == res0b)


def test_serlib_parse_bytestring_new0():
    s = b'(((a b)(c d))((e f)(g h)))'
    address = []
    aux_serlib_parse_bytestring_new(s, address)

def test_serlib_parse_bytestring_new1():
    s = b'(((a b)(c d))((e f)(g h)))'
    address = [1, 0, 1]
    aux_serlib_parse_bytestring_new(s, address)

def test_serlib_parse_bytestring_new2():
    s = b'(((a b)(c))((e f)(g h)))'
    address = [0, 1]
    aux_serlib_parse_bytestring_new(s, address)
    
def test_serlib_parse_bytestring_new3():
    ''' OK '''
    s = b'(((a b)(c))((e f)(g h))(k l)(p q))'
    address = [3, 1]
    aux_serlib_parse_bytestring_new(s, address)

def test_serlib_parse_bytestring_new4():
    ''' expected error for badly formed address '''
    s = b'(((a b)(c))((e f)(g h))(k l)(p q))'
    address = [4, 0]
    with pytest.raises(serlib.cparser.IndexError):
        aux_serlib_parse_bytestring_new(s, address)
    
def test_serlib_parse_bytestring_new5():
    ''' expected error for badly formed address '''
    s = b'(((a b)(c))((e f)(g h))(k l)(p q))'
    address = [3, 2]
    with pytest.raises(serlib.cparser.IndexError):
        aux_serlib_parse_bytestring_new(s, address)


def test_serlib_children():
    s = b'(((a b)(c))((e f)(g h))(k l)(p q))'
    parser = serlib.parser.SExpParser()
    res = parser.postfix_of_bytestring(s)
    ann = serlib.cparser.annotate(res)
    root = res.shape[0] - 1
    children = serlib.cparser.children(res, ann, root)
    pycoq.log.info(f"root node {root} has children {children}")
    assert all(children == [5,12,15,18])





def aux_parse_bytestring(name: str, write=False):
    s = open(with_prefix(f"serlib/{name}.in")).read().strip().encode()
    p = serlib.parser.SExpParser()
    res = numpy.ndarray.tolist(p.postfix_of_bytestring(s))
    if write:
        json.dump(res, open(with_prefix(f"serlib/{name}.out"), 'w'))
    else:
        assert res == json.load(open(with_prefix(f"serlib/{name}.out")))

def test_parse_bytestring():
    aux_parse_bytestring("input0")


def test_parse_inverse2():
    s = open(with_prefix(f"serlib/input2.in")).read()
    p = serlib.parser.SExpParser()
    r = p.postfix_of_sexp(s)
    sprime = p.to_sexp(r)
    sn = numpy.array(list(s))
    sprimen = numpy.array(list(sprime))
    if not (all(sprimen == sn)):
        logging.info(f"{sn[sprimen != sn]}")
        logging.info(f"{sprimen[sprimen != sn]}")
    assert all(sprimen == sn)


def test_hash_bytestring_5gb():
    ''' tests serlib.hash function len 5 Gb '''
    n = 5*2**30
    test = b'\0'*n
    ans = 5371*pow(257, n, 2**64) % 2**64
    assert serlib.parser.hash_bytestring(test) == ans
