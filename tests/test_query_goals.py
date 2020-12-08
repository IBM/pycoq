import pycoq.opam
import pycoq.query_goals
import pycoq.query_goals_legacy
import serlib.parser
import json
import pycoq.log
import logging

def aux_query_goals_legacy(name: str, write=False):
    '''
    tests pycoq.query_goals.parse_serapi_goals(s: str)
    '''
    s = open(f"query_goals/{name}.in").read().strip()
    res = pycoq.query_goals_legacy.parse_serapi_goals(s).to_json()
    
    if write:
        open(f"query_goals/{name}_str.out", 'w').write(res)
    else:
        assert json.loads(res) == json.load(open(f"query_goals/{name}_str.out"))

def aux_query_goals(name: str, output, write=False):
    '''
    tests pycoq.query_goals.parse_serapi_goals(s: str)
    '''
    extension = output.__name__

    input_s = open(f"query_goals/{name}.in").read().strip()
    p = serlib.parser.SExpParser()

    post_fix = p.parse_string(input_s)
    ann = serlib.cparser.annotate(post_fix)

    res = pycoq.query_goals.parse_serapi_goals(p, post_fix, ann, output).to_json()
    
    if write:
        open(f"query_goals/{name}_{extension}.out", 'w').write(res)
    else:
        assert json.loads(res) == json.load(open(f"query_goals/{name}_{extension}.out"))


def test_serapi_installed():
    ''' tests if coq-serapi installation is OK, installs if missing '''
    assert pycoq.opam.opam_install_serapi()


def test_query_goals_legacy():
    aux_query_goals_legacy("input1")

def test_query_goals_str():
    aux_query_goals("input1", str)

def test_query_goals_int():
    aux_query_goals("input1", int)
    
    
