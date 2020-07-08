from dataclasses import dataclass

s = "(ObjList((CoqGoal((goals(((info((evar(Ser_Evar 5))(name())))(ty(Var(Id A)))(hyp((((Id new_id2))()(Prod((binder_name Anonymous)(binder_relevance Relevant))(Var(Id A))(Prod((binder_name Anonymous)(binder_relevance Relevant))(Var(Id B))(Var(Id D)))))(((Id new_id1))()(Var(Id B)))(((Id new_id))()(Var(Id A)))(((Id A)(Id B)(Id D))()(Sort Prop)))))((info((evar(Ser_Evar 6))(name())))(ty(Var(Id B)))(hyp((((Id new_id2))()(Prod((binder_name Anonymous)(binder_relevance Relevant))(Var(Id A))(Prod((binder_name Anonymous)(binder_relevance Relevant))(Var(Id B))(Var(Id D)))))(((Id new_id1))()(Var(Id B)))(((Id new_id))()(Var(Id A)))(((Id A)(Id B)(Id D))()(Sort Prop)))))))(stack())(shelf())(given_up())(bullet())))))"

from pycoq.sexp import sexp

from typing import List, Tuple, Dict

Type = List  # Gallina Expression

class Target():
    def __init__(self, x):
        self.val_ = x
    def __repr__(self):
        return repr(self.val)

class Hyp():
    id: str
    val: list

@dataclass
class Info():
    evar: list
    name: list




@dataclass
class Goal:
    info: Info
    target: Type
    hyp: Dict[str, Tuple[Type,Type]]

    @staticmethod

    def _parse_hyp(h):
        global global_h
        if len(h) == 3:
            vid_list, mid, value = tuple(h)
            for vid in vid_list:
                if (len(vid) == 2 and vid[0] == 'Id' and isinstance(value, list)):
                    yield (vid[1], mid, value)
                else:
                    global_h = h
                    raise ValueError("Error int parsing ids of hypotheses")
        else:
            raise ValueError("Wrong hypotheses tuple length")            
                

    
    @staticmethod
    def _parse_hyp_list(hyp_list):
        if not isinstance(hyp_list, list):
            raise ValueError("Error parsing Hypotheses list from sexp")
        res = dict()
        for h in hyp_list:
            for (key, mid, value) in Goal._parse_hyp(h):
                if not key in res.keys():
                    res[key] = (mid, value)
                else:
                    raise ValueError("Repeating identifier in the hypotheses list")
        return res
                
    @staticmethod
    def from_sexp(se):
        if len(se) == 3:
            info, ty, hyp = se[0], se[1], se[2]
            if (info[0], ty[0], hyp[0]) == ('info', 'ty', 'hyp'):
                a = []
                d = Goal._parse_hyp_list(hyp[1])
                return Goal(info = info[1], target=ty[1], hyp = d)

            
        raise ValueError("Error parsing Goal from sexp")

            

@dataclass
class CoqGoal():
    goals: List[Goal]
    stack: list
    shelf: list
    given_up: list
    bullet: list
    def __init__(self, goals, shelf, stack, given_up, bullet):
        a = []
        for g in goals:
            if isinstance(g, Goal):
                a.append(g)
            else:
                a.append(Goal.from_sexp(g))
        self.goals = a
        self.stack = shelf
        self.shelf = stack
        self.given_up = given_up
        self.bullet = bullet
        
    @staticmethod
    def from_sexp(se):
        if len(se) == 2 and se[0] == 'CoqGoal':
            goals, shelf, stack, given_up, bullet = tuple(se[1])
            if ((goals[0], shelf[0], stack[0], given_up[0], bullet[0]) ==
                'goals', 'shelf', 'stack', 'given_up', 'bullet'):
                return CoqGoal(goals[1], shelf[1], stack[1], given_up[1], bullet[1])
        raise ValueError("Error parsing CoqGoal from sexp")



class ObjList(list):
    def __init__(self, args):
        b = []
        for a in args:
            if isinstance(a, CoqGoal):
                b.append(a)
            else:
                b.append(CoqGoal.from_sexp(a))
        super().__init__(b)


    @staticmethod
    def from_sexp(se):
        if len(se) == 2 and se[0] == 'ObjList':
            return ObjList(se[1])
        else:
            raise ValueError("Error parsing ObjList string from sexp")
        
    
def parse_goals(s: str):
    return ObjList.from_sexp(sexp(s))

if __name__ == '__main__':
    s = open("../goal.error1",'r').read().strip()
    parse_goals(s)
