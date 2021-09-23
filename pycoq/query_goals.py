''' helper functions to parse return of coq-serapi Query () Goals '''

import numpy as np

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import List, Tuple, Optional


import serlib.parser



@dataclass
class SExpr:
    post_fix: np.array
    ann: np.array
    par: serlib.parser.SExpParser
    root: int

    def children(self):
        for child in serlib.cparser.children(self.post_fix, self.ann, self.root):
            yield SExpr(self.post_fix, self.ann, self.par, child)

    
    def __repr__(self):
        return (repr(list(self.children())) if (self.post_fix[self.root] <= 0) else
                self.par.inv_dict[self.post_fix[self.root]].decode())

    def is_leaf(self):
        return self.post_fix[self.root] > 0
    
    

Constr = SExpr
Info = SExpr
Name = SExpr

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
    
    def empty(self) -> bool:
        return len(self.goals) == 0 and len(self.stack) == 0 and len(self.shelf) == 0
        


def srepr(par: serlib.parser.SExpParser, post_fix, ann, root, output) -> str:
    if root == None:
        return None
    if output == str:
        start_pos = ann[root]
        end_pos = root + 1
        return par.to_sexp(post_fix[start_pos:end_pos])
    elif output == int:
        if isinstance(root, int):
            return root
        elif isinstance(root, np.int32):
            return root.item()
        else:
            raise ValueError(f"Root type of {root} is not int nor numpy.int32 for compressed int repr")
    else:
        return SExpr(post_fix, ann, par, root)
        




def parse_ids(par, post_fix, ann, root, output) -> List[Name]:
    '''
    returns a list of id names
    '''
    id_list = serlib.cparser.children(post_fix, ann, root).tolist()
    return [srepr(par, post_fix, ann, id, output) for id in id_list]

def parse_hyp(par, post_fix, ann, root, output) ->Hyp:
    '''
    returns a hypotheses
    '''
    _ids, _define, _typ = serlib.cparser.children(post_fix, ann, root).tolist()
    _define = serlib.cparser.children(post_fix, ann, _define).tolist()
    if len(_define) == 0:
        _define = None
    elif len(_define) > 1:
        raise ValueError(f"definition of hypothesis does not match Optional")
    else:
        _define = _define[0]
    return Hyp(ids=parse_ids(par, post_fix, ann, _ids, output), define=srepr(par, post_fix, ann, _define, output), typ=srepr(par, post_fix, ann, _typ, output))
        

def parse_list_hyp(par, post_fix, ann, list_hyp, output) -> List[Hyp]:
    '''
    returns a list of hypotheses
    '''
    _hyps = serlib.cparser.children(post_fix, ann, list_hyp).tolist()
    return [parse_hyp(par, post_fix, ann, _hyp, output) for _hyp in _hyps]

def parse_rgoal(par, post_fix, ann, root, output) -> RGoal:
    ''' 
    returns reified goal
    '''
    _info, _ty, _list_hyp = serlib.cparser.children(post_fix, ann, root).tolist()

    head, info = serlib.cparser.children(post_fix, ann, _info).tolist()
    if par.to_sexp([post_fix[head]]) != 'info':
        raise ValueError("the input field {_info} does not match info")

    
    head, ty = serlib.cparser.children(post_fix, ann, _ty).tolist()
    if par.to_sexp([post_fix[head]]) != 'ty':
        raise ValueError("the input field {_ty} does not match ty")

    head, list_hyp = serlib.cparser.children(post_fix, ann, _list_hyp).tolist()
    if par.to_sexp([post_fix[head]]) != 'hyp':
        raise ValueError("the input field {_list_hyp} does not match hyp")

    return RGoal(info=srepr(par, post_fix, ann, info, output),
                 target=srepr(par, post_fix, ann, ty, output),
                 hyp=parse_list_hyp(par, post_fix, ann, list_hyp, output))

def parse_goals(par, post_fix, ann, node, output):
    '''
    returns a list of reified goals
    '''
    goals = serlib.cparser.children(post_fix, ann, node).tolist()
    return [parse_rgoal(par, post_fix, ann, goal, output) for goal in goals]



def parse_stack(par, post_fix, ann, root, output) -> List[Tuple[List[RGoal], List[RGoal]]]:
    '''
    stack of goal views is implemented as a list
    focusing on a goal moves other goals from a current view on top of the stack

    a stack element consists of hidden view goals
    it is implemented as a pair of List of RGoals
    
    the second element of the pair is a hidden view at a given stack depth
    consisting of the list of goals
    '''
    items = serlib.cparser.children(post_fix, ann, root).tolist()
    res = []
    for item in items:
        _first, _second = serlib.cparser.children(post_fix, ann, item).tolist()
        first = parse_goals(par, post_fix, ann, _first, output)
        second = parse_goals(par, post_fix, ann, _second, output)
        res.append((first, second))
    return res


def parse_serapi_goals(par: serlib.parser.SExpParser,
                       post_fix: np.ndarray,
                       ann: np.ndarray,
                       output: type) -> SerapiGoals:
    '''

    parses the return of coq-serapi command Query () Goals
    according to the specification in 
    https://github.com/ejgallego/coq-serapi/blob/v8.13/serapi/serapi_protocol.ml
    https://github.com/ejgallego/coq-serapi/blob/v8.13/serapi/serapi_goals.ml


    Query () Goals returns [CoqGoal g]

    CoqGoal of Constr.t serapi_goals.reified_goal serapi_goals.ser_goals
    
    type 'a hyp = (Names.Id.t list * 'a option * 'a)

    type info =
    { evar : Evar.t
    ; name : Names.Id.t option
    }

    type 'a reified_goal =
    { info : info
    ; ty   : 'a
    ; hyp  : 'a hyp list
    }

    type 'a ser_goals =
    { goals : 'a list
    ; stack : ('a list * 'a list) list
    ; shelf : 'a list
    ; given_up : 'a list
    ; bullet : Pp.t option
    }
    '''

    root = ann.shape[0] - 1
    head, args = serlib.cparser.children(post_fix, ann, root).tolist()
    if par.to_sexp([post_fix[head]]) != 'ObjList':
        raise ValueError("the input s-expression does not match ObjList")

    goal = serlib.cparser.children(post_fix, ann, args).tolist()
    if len(goal) == 0:
        return None
    if len(goal) != 1:
        raise ValueError(f"the input :{input_s}: does not match [CoqGoal g] specification")

    coq_goal = goal[0]
    head, args = serlib.cparser.children(post_fix, ann, coq_goal).tolist()

    if par.to_sexp([post_fix[head]]) != 'CoqGoal':
        raise ValueError(f"the input {coq_goal}  not match CoqGoal()")

    args = serlib.cparser.children(post_fix, ann, args).tolist()

    if len(args) != 5:
        raise ValueError(f"can't match {len(args)} with goals, stack, shelf, given_up, bullet")

    _goals, _stack, _shelf, _given_up, _bullet = args

    head, goals = serlib.cparser.children(post_fix, ann, _goals)
    if par.to_sexp([post_fix[head]]) != 'goals':
        raise ValueError(f"can't match {head} with goals")

    head, stack = serlib.cparser.children(post_fix, ann, _stack)
    if par.to_sexp([post_fix[head]]) != 'stack':
        raise ValueError(f"can't match {head} with stack")
        
    head, shelf = serlib.cparser.children(post_fix, ann, _shelf,)
    if par.to_sexp([post_fix[head]]) != 'shelf':
        raise ValueError(f"can't match {head} with shelf")

    head, given_up = serlib.cparser.children(post_fix, ann,_given_up)
    if par.to_sexp([post_fix[head]]) != 'given_up':
        raise ValueError(f"can't match {head} with given_up")

    head, bullet = serlib.cparser.children(post_fix, ann,_bullet)
    if par.to_sexp([post_fix[head]]) != 'bullet':
        raise ValueError(f"can't match {head} with bullet")

    return SerapiGoals(goals=parse_goals(par, post_fix, ann, goals, output),
                       stack=parse_stack(par, post_fix, ann, stack, output),
                       shelf=parse_goals(par, post_fix, ann, shelf, output),
                       given_up=parse_goals(par, post_fix, ann, given_up, output),
                       bullet=srepr(par, post_fix, ann, bullet, output))

