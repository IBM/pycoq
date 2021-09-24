import asyncio
import os

import pycoq.opam
import pycoq.common
import pycoq.agent

import pkg_resources

def with_prefix(s: str) -> str:
    ''' adds package path as prefix '''
    return os.path.join(pkg_resources.resource_filename('pycoq', 'test'), s)

def test_serapi_installed():
    ''' tests if coq-serapi installation is OK, installs if missing '''
    assert pycoq.opam.opam_install_serapi()


def test_autoagent3():
    ''' tests autoegent at depth 3 '''
    coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(), executable='', target='serapi_shell')
    cfg = pycoq.opam.opam_serapi_cfg(coq_ctxt)

    res, defi = asyncio.run(
        pycoq.agent.evaluate_agent(
            cfg, pycoq.agent.auto_agent,
            "Theorem th_4_2_9: forall A B C D: Prop, A->(A->B)->(B->C)->(C->D)->D.",
            "th_4_2_9",
            agent_parameters={'auto_limit':3},
            logfname = with_prefix('autoagent/agent3.log')))
                      
    print("########################## res is ", res)
    print(with_prefix('autoagent/agent3.log'))
    assert res == -1 # -1 stands for fail to proof 


def test_autoagent10():
    ''' tests autoegent at depth 10 '''
    coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(), executable='', target='serapi_shell')
    cfg = pycoq.opam.opam_serapi_cfg(coq_ctxt)

    res, defi = asyncio.run(pycoq.agent.evaluate_agent(cfg, pycoq.agent.auto_agent,
                     "Theorem th_4_2_9: forall A B C D: Prop, A->(A->B)->(B->C)->(C->D)->D.", 
                                                 "th_4_2_9",
                                                 agent_parameters={'auto_limit':5},
                      logfname=with_prefix('autoagent/agent10.log')))

    assert res == 4  # correct depth of proof is 4
    
def test_autoagent_error_0():
    ''' tests autoagent parsing error '''
    coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(), executable='', target='serapi_shell')
    cfg = pycoq.opam.opam_serapi_cfg(coq_ctxt)

    res, defi = asyncio.run(
        pycoq.agent.evaluate_agent(
            cfg, pycoq.agent.auto_agent,
            "Theorem th_4_2_9: forall A B C D: Prop, A->(A->B)->(B->C)->(C->D)->F.", 
            "th_4_2_9",
                     agent_parameters={'auto_limit':10},
            logfname=with_prefix('autoagent/agent0.log')))
            
    assert res == -2 # -2 stands for the parsing error

    
def test_autoagent_error_1():
    ''' tests autoagent parsing error '''
    cfg = pycoq.opam.opam_serapi_cfg()

    input_line = (r"messed up input very bad239 235()*&*(^%(^PU afds ;Y a\sf\\a\sd\f asdf\\ )) "
                  r"should not crash but return -2")

    res, defi = asyncio.run(
        pycoq.agent.evaluate_agent(
            cfg, pycoq.agent.auto_agent,
            input_line,
            "",
                     agent_parameters={'auto_limit':10},
            logfname=with_prefix('autoagent/agent1.log')))
            
    assert res == -2 # -2 stands for the parsing error
