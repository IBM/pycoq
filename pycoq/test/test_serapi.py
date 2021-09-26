'''
sample test of pycoq
'''
import os
import asyncio
import logging

import concurrent.futures

import pycoq.opam
import pycoq.config
import pycoq.log
import pycoq.query_goals
import sys

import pkg_resources

def with_prefix(s: str) -> str:
    ''' adds package path as prefix '''
    return os.path.join(pkg_resources.resource_filename('pycoq', 'test'), s)


def format_query_goals(steps) -> str:
    ''' formats output of pycoq.opam.opam_coq_serapi_query_goals '''
    ans = ""
    for i, step in enumerate(steps):
        stmt, _serapi_goals, serapi_goals = step
        ans += f"step {i}\n"
        ans += f"input: {stmt}\n"
        ans += f"query: {_serapi_goals}\n"
        ans += f"parsed: {serapi_goals}\n"
    return ans


def check_ans(ans: str, project: str, fname: str, write=False):
    ''' checks results against saved '''
    dirname = os.path.join(with_prefix(project),os.path.dirname(fname))
    print(f"dirname is {dirname}")
    if write:
        os.makedirs(dirname, exist_ok=True)
        with open(os.path.join(dirname,os.path.basename(fname)), 'w') as stream:
            stream.write(ans)
    with open(os.path.join(dirname,os.path.basename(fname)), 'r') as stream:
        assert ans == stream.read()
        

def aux_query_goals_single(coq_package: str, coq_package_pin=None, write=False):
    ''' tests coq package againss cparser + query_goals '''
    logging.info(f"ENTERED aux_query_goals")
    for filename in pycoq.opam.opam_strace_build(coq_package, coq_package_pin):
        logging.info(f"PROCESSING {filename}")
        ctxt = pycoq.common.load_context(filename)
        steps = asyncio.run(pycoq.opam.opam_coq_serapi_query_goals(ctxt))

        ans = format_query_goals(steps)
        check_ans(ans, coq_package, ctxt.target + '._pytest_signature_query_goals',
                  write=write)

def _query_goals(ctxt):
    return asyncio.run(pycoq.opam.opam_coq_serapi_query_goals(ctxt))

def aux_query_goals(coq_package: str, coq_package_pin=None, write=False):
    ''' tests coq package againss cparser + query_goals '''

    logging.info(f"ENTERED aux_query_goals")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {}
        for filename in pycoq.opam.opam_strace_build(coq_package, coq_package_pin):
            logging.info(f"MULTI-PROCESSING STARTED: {filename}")
            ctxt = pycoq.common.load_context(filename)
            futures[executor.submit(_query_goals, ctxt)] = ctxt

        for fut in concurrent.futures.as_completed(futures):
            ctxt = futures[fut]
            steps = fut.result()
            logging.info(f"MULTI-PROCESSING FINISHED: {ctxt.target}")
            ans = format_query_goals(steps) 
            check_ans(ans, coq_package, ctxt.target + '._pytest_signature_query_goals',
                      write=write)

def aux_lf_query_goals(write=False):
    sys.setrecursionlimit(10000)
    print("recursion limit", sys.getrecursionlimit())
    aux_query_goals("lf", f"file://{with_prefix('lf')}", write=write)


def aux_bignums_query_goals(write=False):
    aux_query_goals("coq-bignums",  write=write)


def test_serapi_installed():
    ''' tests if coq-serapi installation is OK, installs if missing '''
    assert pycoq.opam.opam_install_serapi()


def test_lf_query_goals(benchmark):
    benchmark.pedantic(aux_lf_query_goals)

#def test_bignums_query_goals(benchmark):
#    benchmark.pedantic(aux_bignums_query_goals)
