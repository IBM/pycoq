import pkg_resources
import os

import pycoq.opam
import pycoq.query_goals
import serlib.parser
import json
import pycoq.log
import logging



def with_prefix(s: str) -> str:
    ''' adds package path as prefix '''
    return os.path.join(pkg_resources.resource_filename('pycoq', 'test'), s)


def aux_query_goals(name: str, output, write=False):
    '''
    tests pycoq.query_goals.parse_serapi_goals(s: str)
    '''
    extension = output.__name__

    input_s = open(with_prefix(f"query_goals/{name}.in")).read().strip()
    p = serlib.parser.SExpParser()

    post_fix = p.postfix_of_sexp(input_s)
    ann = serlib.cparser.annotate(post_fix)

    res = pycoq.query_goals.parse_serapi_goals(p, post_fix, ann, output).to_json()
    
    if write:
        open(with_prefix(f"query_goals/{name}_{extension}.out"), 'w').write(res)
    else:
        assert json.loads(res) == json.load(open(with_prefix(f"query_goals/{name}_{extension}.out")))


def test_serapi_installed():
    ''' tests if coq-serapi installation is OK, installs if missing '''
    assert pycoq.opam.opam_install_serapi()


def test_query_goals_str():
    aux_query_goals("input1", str)

def test_query_goals_int():
    aux_query_goals("input1", int)
    
    
