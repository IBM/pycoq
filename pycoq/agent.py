import pycoq.serapi
import pycoq.log

import serlib.parser

from serlib.parser import SExpParser

from typing import Iterable, List, Tuple

DEBUG = True

def debug(*args):
    if DEBUG:
        print(*args)
    

    
async def evaluate_agent_on_stream(cfg: pycoq.common.LocalKernelConfig, agent, props: Iterable[str],
                                   agent_parameters = {}, section_name = "section0000", logfname=None):
    async with pycoq.serapi.CoqSerapi(cfg, logfname=logfname) as coq:
        for prop in props:
            result = await coq.execute(f"Section {section_name}.")
            last_sids = result[3]
            if (len(last_sids) != 1 or len(result[2]) > 0):
                print("evaluate_agent_session: coq execute result is", result)
                raise RuntimeError("evaluate_agent_session: new section was not initialized, aborting..")
                
            result = await coq.execute(prop)
            
            if len(result[2]) > 0:
                debug("evaluate_agent_session: Error in proposition")
                debug(result[2])
                yield (prop, -2)
            else:
                agent_result = await agent(coq, **agent_parameters)
                
                result = await coq.cancel_completed(last_sids)

                debug("evaluate_agent_session: most recent agent section cancelled; ready to evaluate another proposition")
                yield (prop, agent_result)    

                
async def evaluate_agent_in_session(coq: pycoq.serapi.CoqSerapi, par, agent, prop: str, agent_parameters = {}):

    result = await coq.execute(prop)
    last_sids = result[3]
    if len(last_sids) != 1 or len(result[2]) > 0:
        debug("evaluate_agent_in_session: Error in proposition")
        debug(result[2])
        return -2
    else:
        
        agent_result = await agent(coq, **agent_parameters)

        result = await coq.cancel_completed(last_sids)

        debug("evaluate_agent_session: most recent section cancelled; ready to evaluate another proposition")
        return agent_result
    
    
    
    
    
                
                
    
async def evaluate_agent(cfg: pycoq.common.LocalKernelConfig, agent, prop: str, name: str, agent_parameters = {}, logfname=None):
    """
    input: 
    prop: proposition statement in coq - gallina grammar on a single line"
    agent: coq_env -> coq_env 

    creates coq env and loads the proposition statement 
    calls agent and pass env to the agent
    awaits when agent returns the env
    
    returns (error_code, definition)
    #  (0,  definition) success returned 
    #  (-1, None)       failure returned
    #  (-2, None) agent was not called because coq did not parse the theorem statement
    """

    async with pycoq.serapi.CoqSerapi(cfg, logfname=logfname) as coq:
        result = await coq.execute(prop)
        if len(result[2]) > 0:
            debug("evaluate_agent: Error in proposition")
            debug(result[2])
            return (-2, None)
        else:
            result = await agent(coq, **agent_parameters)
            if result < 0:
                return (result, None)
            definition = await coq.query_definition_completed(name)
            return (result, definition)


            
        
        
        
        
            
async def get_goals_stack(coq):
    parser = coq.parser
    goals = await coq.query_goals_completed()
    goals_stack = parser.postfix_of_sexp(goals,[1,0,1,0,1])
    if len(goals_stack) == 0:
        raise RuntimeError("Error: bad environment response on the agent side"
                           "The goals object is not returned from serapi query goals")
    else:
        return goals_stack

def time_space_bounds_ok(cnt, cnt_limit):
    """
    this is silly template function that checks that 
    space time bounds for RL / DFS / MCTS agent are satisfied 
    
    for now it checks that we have positive number of steps to try
    
    in future we should check that we did not exceed limited memory and time resources allocated to agent
    """

    return cnt < cnt_limit

    
async def auto_agent(coq: pycoq.serapi.CoqSerapi, auto_limit: int):
    """
    default agent that tries to solve the problem in cnt steps using the tactics auto
    on iteration i agent will execute auto i tactics
    """
    parser = SExpParser()

    cnt = 0
    
    goals_stack = await get_goals_stack(coq)
        
    while time_space_bounds_ok(cnt, auto_limit):
        debug(f"agent: have {-goals_stack[-1]} goals to solve")
            
        # the main code of RL / DFS / MCTS agent will go here 
        # given the goal stack the agent needs to decide what command to execute on coq engine

        debug("agent: trying default auto tactics")
        result = await coq.execute(f"auto {cnt}.")
        debug(f"agent: auto {cnt} tactic is completed with result", result)

        goals_stack = await get_goals_stack(coq)   #prepare the goals stack for the next round 
        if (goals_stack[-1] == 0):
            debug(f"agent: Success, all goals are solved with auto {cnt}.")
            _, _, coq_exc, _ = await coq.execute("Qed.")
            if coq_exc:
                pycoq.log.info(f"evaluation of Qed. in coq-serapi session raised exception {coq_exc}")
            return cnt
        cnt += 1
            
    debug("agent: Failure, time space bounds exceeded")
    return -1
            
async def deterministic_agent(coq: pycoq.serapi.CoqSerapi, proof_script: List[str], par) -> Tuple[int, int]:
    """
    deterministic agent that executes a given proof_script in open session coq
    returns (n_steps, n_goals) where
    n_steps is the number of steps successfully executed
    n_goals is the number of goals left after execution of n_steps
    """

    goals_stack = await get_goals_stack(coq)

    pycoq.log.debug(f"deterministic_agent has {-goals_stack[-1]} goals to solve")

    
    
    n_steps = 0
    print(proof_script)
    for stmt in proof_script:
        print("executing ", stmt)
        _, _, coq_exc, _ = await coq.execute(stmt)

        if coq_exc:
            print(f"evaluation of {stmt} in coq-serapi session raised exception {coq_exc}")
            break

        n_steps += 1
        _serapi_goals = await coq.query_goals_completed()
            
        post_fix = par.postfix_of_sexp(_serapi_goals)
        ann = serlib.cparser.annotate(post_fix)
        
        s = pycoq.query_goals.srepr(par, post_fix, ann, len(post_fix) - 1, str)
        print(s)
        serapi_goals = pycoq.query_goals.parse_serapi_goals(par, post_fix, ann, pycoq.query_goals.SExpr)
            
        
        
        
        if len(serapi_goals.children()) == 0:
            print("goals stack [-1] = 0")
            break

    # finalize

    stmt = "Qed." if goals_stack[-1] == 0 else "Abort."
    _, _, coq_exc, _ = await coq.execute(stmt)
    if coq_exc:
        pycoq.log.info(f"evaluation of {stmt} in coq-serapi session raised exception {coq_exc}")
            
    return (n_steps, -goals_stack[-1])


