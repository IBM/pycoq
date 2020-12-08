''' helper functions to parse return of coq-serapi Query () Goals '''

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import List, Tuple, Optional

import serlib.parser
import logging

Constr = str
Info = str
Name = str

@dataclass_json
@dataclass
class Hyp:
    '''
    coq-serapi/serlib/ser_goals.ml 'a hyp = (Names.Id.t list * 'a option * 'a)
    '''
    ids: List[Name]
    define: Optional[Constr]
    typ: Constr

@dataclass_json
@dataclass
class RGoal:
    '''
    coq-serapi/serlib/ser-goals  type Constr.t reified_goal
    '''
    info: Info
    target: Constr
    hyp: List[Hyp]

@dataclass_json
@dataclass
class SerapiGoals:
    ''' coq-serapi/serlib/ser_goals.ml   type Constr.t reified_goal ser_goals '''
    goals: List[RGoal]
    stack: List[Tuple[List[RGoal], List[RGoal]]]
    shelf: List[RGoal]
    given_up: List[RGoal]
    bullet: Optional[str]


def parse_ids(_ids) -> List[Name]:
    '''
    returns a list of id names 
    '''
    id_list = serlib.parser.list_of_string(_ids)
    return id_list


def parse_hyp(input_s: str) -> Hyp:
    ''' 
    returns a hypotheses
    '''
    _ids, _define, _typ = serlib.parser.list_of_string(input_s)
    _define = serlib.parser.list_of_string(_define)
    if len(_define) == 0:
        _define = None
    elif len(_define) > 1:
        raise ValueError(f"definition of {_define} hypothesis does not match Optional")
    else:
        _define = _define[0]
    return Hyp(ids=parse_ids(_ids), define=_define, typ=_typ)



def parse_list_hyp(input_s: str) -> List[Hyp]:
    '''
    returns a list of hypotheses
    '''
    _hyps = serlib.parser.list_of_string(input_s)
    return [parse_hyp(_hyp) for _hyp in _hyps]




def parse_rgoal(input_s: str) -> RGoal:
    '''
    returns reified goal
    '''

    _info, _ty, _list_hyp = serlib.parser.list_of_string(input_s)
    head, info = serlib.parser.list_of_string(_info)
    if head != 'info':
        raise ValueError("the input field {head} does not match info")

    head, ty = serlib.parser.list_of_string(_ty)
    if head != 'ty':
        raise ValueError("the input field {head} does not match ty")

    head, list_hyp = serlib.parser.list_of_string(_list_hyp)
    if head != 'hyp':
        raise ValueError("the input field {head} does not match hyp")

    return RGoal(info=info, target=ty, hyp=parse_list_hyp(list_hyp))


def parse_goals(input_s: str) -> List[RGoal]:
    ''' 
    returns a list of reified goals
    '''
    goals = serlib.parser.list_of_string(input_s)
    return [parse_rgoal(goal) for goal in goals]


def parse_stack(input_s: str) -> List[Tuple[List[RGoal], List[RGoal]]]:
    '''
    stack of goal views is implemented as a list
    focusing on a goal moves other goals from a current view on top of the stack

    a stack element consists of hidden view goals
    it is implemented as a pair of List of RGoals
    
    the second element of the pair is a hidden view at a given stack depth
    consisting of the list of goals
    '''
    items = serlib.parser.list_of_string(input_s)
    res = []
    for item in items:
        _first, _second = serlib.parser.list_of_string(item)
        first = parse_goals(_first)
        second = parse_goals(_second)
        res.append((first, second))
    return res



# def node_index(post_fix, ann, address) -> int:
#     ''' return node index by address '''
#     start_pos, end_pos = serlib.cparser.subtree(post_fix, ann, address)
#     return end_pos - 1



def parse_serapi_goals(input_s: str) -> SerapiGoals:
    
    head, args = serlib.parser.list_of_string(input_s)
    if head != 'ObjList':
        raise ValueError("the input s-expression does not match ObjList")
    goal = serlib.parser.list_of_string(args)
    if len(goal) == 0:
        return None
    if len(goal) != 1:
        raise ValueError(f"the input :{input_s}: does not match [CoqGoal g] specification")

    coq_goal = goal[0]
    head, args = serlib.parser.list_of_string(coq_goal)

    if head != 'CoqGoal':
        raise ValueError(f"the input {coq_goal}  not match CoqGoal()")

    args = serlib.parser.list_of_string(args)

    if len(args) != 5:
        raise ValueError(f"can't match {len(args)} with goals, stack, shelf, given_up, bullet")
    
    _goals, _stack, _shelf, _given_up, _bullet = args

    head, goals = serlib.parser.list_of_string(_goals)
    if head != 'goals':
        raise ValueError(f"can't match {head} with goals")

    head, stack = serlib.parser.list_of_string(_stack)
    if head != 'stack':
        raise ValueError(f"can't match {head} with stack")

    head, shelf = serlib.parser.list_of_string(_shelf)
    if head != 'shelf':
        raise ValueError(f"can't match {head} with shelf")

    head, given_up = serlib.parser.list_of_string(_given_up)
    if head != 'given_up':
        raise ValueError(f"can't match {head} with given_up")

    head, bullet = serlib.parser.list_of_string(_bullet)
    if head != 'bullet':
        raise ValueError(f"can't match {head} with bullet")

    return SerapiGoals(goals=parse_goals(goals),
                       stack=parse_stack(stack),
                       shelf=parse_goals(shelf),
                       given_up=parse_goals(given_up),
                       bullet=bullet)
