""" test script agent in pycoq 
"""
import asyncio
import os

from typing import Iterable

import pycoq.opam
import pycoq.common
import pycoq.agent


async def tutorial_deterministic_agent(theorems: Iterable):
    """
    a snipped of code demonstrating usage of pycoq
    """

    # create default coq context for evaluation of a theorem
    coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(),
                                       executable='',
                                       target='serapi_shell')
    cfg = pycoq.opam.opam_serapi_cfg(coq_ctxt)


    # create python coq-serapi object that wraps API of the coq-serapi  
    async with pycoq.serapi.CoqSerapi(cfg) as coq:
        for prop, script in theorems:

            # execute proposition of the theorem
            _, _, coq_exc, _ = await coq.execute(prop)
            if coq_exc:
                print(f"{prop} raised coq exception {coq_exc}")
                continue

            # execute the proof script of the theorem
            n_steps, n_goals = await pycoq.agent.script_agent(coq, script)

            msg = f"Proof {script} fail" if n_goals != 0 else f"Proof {script} success"
            print(f"{prop} ### {msg} in {n_steps} steps\n")


def main():

    theorems = [
        ("Theorem th4: forall A B C D: Prop, A->(A->B)->(B->C)->(C->D)->D.",
         ["auto."]),
        ("Theorem th5: forall A B C D E: Prop, A->(A->B)->(B->C)->(C->D)->E.",
         ["auto."]),
        ("Theorem th6: forall A B C D E: Prop, A->(A->B)->(B->C)->(C->D)->(D->E)->E.",
         ["auto."])]
        

    asyncio.run(tutorial_deterministic_agent(theorems))

if __name__ == '__main__':
    main()
    
    


            
