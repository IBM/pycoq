import os
import asyncio
import io
import aiofile
import sys
import argparse
import concurrent.futures
import tqdm
import multiprocessing
import datetime
import time
import json


import pycoq.common
import pycoq.kernel
import pycoq.serapi
import pycoq.split
import pycoq.parse

# https://rgxdb.com/r/5FZS9VWD
# double quote escaping double quote

from typing import Optional





def serapi_log_fname(source):
    return source + pycoq.common._DEFAULT_SERAPI_LOGEXT


async def printlines(aiter):
    async for line in aiter:
        print(line, end='')


async def process(source, args):
    async with aiofile.AIOFile(source, 'rb') as inp:
        coq_stmts = pycoq.split.agen_coq_stmts(aiofile.LineReader(inp))

        coq_ctxt = pycoq.common.load_context(pycoq.common.context_fname(source), quiet=True)
        ser_args = pycoq.common.serapi_args(coq_ctxt.IQR())
        ser_args = ser_args + ['--topfile', source]
        cfg = pycoq.common.serapi_kernel_config(pwd=coq_ctxt.pwd, args=ser_args)

        errors = []

        if args.save_serapi_log:
            logfname = serapi_log_fname(source)
        async with pycoq.serapi.CoqSerapi(cfg, logfname=logfname) as coq:
            async for coq_stmt in coq_stmts:
                cmd_tag, resp_ind, coqexns, sids = await coq.execute(coq_stmt)
                errors.extend(coqexns)

                goals = await coq.query_goals_completed()
                for g in goals:
                    try:
                        #parsed = pycoq.parse.parse_goals(g)
                        pass
                    except ValueError as exc:
                        print("=========ERROR======== in ", source, coq_stmt)
                        with open('goal.error','w') as ferror:
                            print("===ERROR=== in ", source, coq_stmt, file=ferror)
                            print("===GOALS===", file=ferror)
                            print(g, file=ferror)
                        sys.exit(-1)

                    
                    
                    
                        
                        

        msg = (f"sent {len(coq._sent_history)}, "
               f"exec {len(coq._executed_sids)}")

        if errors == []:
            return (source, "OK:" + msg)
        else:
            return (source, f"ERRORS: {errors} " + msg)


def run_task(source, args):
    return asyncio.run(process(source, args))

def record(flog, source, res):
    print(f"{source}: ", end='',file=flog)
    print(f"{res}", file=flog)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workdir', type=str, default=os.getcwd())
    parser.add_argument('source', type=str)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--log', type=str, default='/dev/stdout')
    parser.add_argument('--with-context', action='store_true',
                        help='process only source files with '
                        'for which pycoq context files exist')
    parser.add_argument('--save-serapi-log', action='store_true',
                        help=f'save detailed serapi logs in source filename + {pycoq.common._DEFAULT_SERAPI_LOGEXT}')
    args = parser.parse_args()

    sources = []
    source = os.path.abspath(args.source)
    if os.path.isfile(source):
        sources.append(source)

    elif os.path.isdir(source):
        print(f"Processing {source}")
        sources_gen = pycoq.common.find_files(source, r".*\.v$")
        for source in sources_gen:
            if not args.with_context or os.path.isfile(pycoq.common.context_fname(source)):
                sources.append(source)

    if not sources:
        print("Input is empty")
        sys.exit(0)
    else:
        print(f"Processing {len(sources)} sources")

    print(f"Log file: {args.log}")

    prof_stat = []
    with open(args.log,'w') as flog:
        pass
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_task, source, args) for source in sources]
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(sources), miniters=1):
            with open(args.log, 'a') as flog:
                cdt = datetime.datetime.fromtimestamp(time.time()).isoformat()
                print(f"{cdt} run {args}",  file=flog)
                source, res = future.result()
                record(flog, source, res)



if __name__ == '__main__':
    main()
