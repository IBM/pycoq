# interface to coq (coq-serapi) from python
# consider switching to pypy for performance 
# using python parsing library lark https://github.com/lark-parser/lark to parse sexp 
# https://pypi.org/project/lark-parser/
# pip install lark-parser



# TODO: consider switching to https://docs.python.org/3/library/select.html instead of custom
# timeout queue implementation  https://pymotw.com/2/select/

# TODO: https://www.semicolonworld.com/question/42796/non-blocking-read-on-a-subprocess-pipe-in-python

DEBUG_ERRORS = 3
DEBUG_RESPONSE = 1

import tqdm
import io
import sys, os
import re
import argparse
import threading
import logging
from typing import List
import time
import subprocess
import queue


from pathos.multiprocessing import _ProcessPool as Pool
#from multiprocessing import Pool 

from lark_serapi import sexp_parser_mach as sexp_parser  # we define sexp parser there

from lark_serapi import (ocaml_string_quote, serapi_type,
                         serapi_answer_entry, left_value,
                         serapi_answer_status,
                         serapi_added_entry)

from extract_locations import loc_of_sexp

from utils import (find, VERNAC_FILE,
                   session_context_from_coqlog,
                   session_context_from_args,
                   SessionContext,
                   SessionJob)


def completed_resp(resp):
    try:
        rs=sexp_parser.parse(resp)
        if serapi_type(rs)=='Answer' and serapi_answer_status(rs)=='Completed':
            return True
    except Exception:
        print("#### error parsing", resp)

    return False
    
class Coq():
    def __init__(self, gc: GContext, p: Prop) -> bool:
        ''' instatiate coq session, perhaps on a remote server with pipe communication '''
        self._state = set()

    def state(self) -> State:
        ''' retrieves state from coq '''
        return self.state

    def act(self, a: Action) -> None:
        pass
    

class CoqSession(threading.Thread):
    # sc: SessionContext contains the LoadPath coq options -I -Q -R
    # and the command working directory from which coq interpretor should be run
    
    # we'll override the __init__ and __run__ methods of Thread
    # the thread will be started in the __init__ by the Thread start() 
    # thread finishes when run() terminates
    # https://docs.python.org/3.8/library/threading.html
    # https://realpython.com/intro-to-python-threading/
    # daemon = True: kill the thread automatically when terminating the main program
    # without waiting for the thread to finish its computation
    # join() waits until the thread finishes its computation
    
    def  __init__(self, sc: SessionContext, debug=0, log_file = sys.stderr):
        threading.Thread.__init__(self, daemon=True)
        self.log_file = log_file
        self.debug = debug
        # assume that serapi comunicates in utf8
        self._process = subprocess.Popen(["sertop", "--printer=mach"]+sc.serapi_args(),
                                          cwd=sc.cwd(),
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          encoding='utf8')
        
        self._out = self._process.stdout
        self._in = self._process.stdin
        self._err = self._process.stderr

        self._responses = queue.Queue()  #  queue of responses from sertop
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not (exc_type==None and exc_val==None and exc_tb==None):
            print('sertop terminated because of', exc_type, exc_val, exc_tb)
        self._process.terminate()
        
        
        

    def send_serapi_command(self, cmd : str):
        self._in.write(cmd)
        self._in.flush()


    def run(self) -> None:
        #print("running thread {}".format(threading.get_ident()))
        line = None
        while line != '':
            line = self._out.readline()
            self._responses.put(line.strip())
        self.end_of_output()
            
    def end_of_output(self):
        if self.debug >= DEBUG_ERRORS:
            print("End of sertop output is reached, thread {}".format(threading.get_ident()))
            print("Waiting for sertop proc to finish in thread {}...".format(threading.get_ident()))
        self._process.wait()
        assert self._process.poll() is not None
        if self.debug >= DEBUG_ERRORS:
            print("Sertop has finished with exit code {}...".format(self._process.poll()))
            print("Sertop stderr is")
            print(self._err.read())


    def get_response(self, timeout=2):
        return self._responses.get(timeout=timeout)
            
    def get_responses(self, size=-1, timeout=2, finish_fun = lambda x: True):
        counter = 0
        while (counter < size) or (size < 0) or (size is None):
            try:
                r = self.get_response(timeout=timeout)
                yield r
                counter += 1
                assert not finish_fun(r)
            except Exception:
                break

    def get_presponses(self, size=-1, timeout=2, finish_fun = lambda x: True):
        for resp in self.get_responses(size=size,timeout=timeout,finish_fun=finish_fun):
            try:
                yield (sexp_parser.parse(resp), resp)
            except Exception as exc:
                print("ERROR parsing because of",exc, resp, file=self.log_file)
            

    def send_add(self, s:str):
        serapi_cmd = '(Add () "{}")'.format(ocaml_string_quote(s))
        self.send_serapi_command(serapi_cmd)

    def execute(self, index:int):
        serapi_cmd = "(Exec {})".format(index)
        self.send_serapi_command(serapi_cmd)

    def goals(self, index:int):
        serapi_cmd = "(Query ((sid {})) Goals)".format(index)
        self.send_serapi_command(serapi_cmd)
        prs = list(self.get_presponses(finish_fun = completed_resp))
        if len(prs) != 3:
            print("ERROR in Query, received serapi responses {} PRS".format(len(prs)), file=self.log_file)
        else:
            try:
                for rs,s in prs:
                    assert serapi_type(rs) == 'Answer'
                    if serapi_answer_status(rs) == 'ObjList':
                        yield rs,s
            except Exception as exc:
                print("ERROR in Querry Goals", exc)

                        
                
                

    def __del__(self):
        self._process.terminate()


def safe_loc(sout):
    try: 
        p = loc_of_sexp(sexp_parser.parse(sout.strip()))
    except Exception:
        p = (None,None)
    return p



def loc_list_of_vernac(fname: str, sc: SessionContext, log_file=sys.stderr):
    proc = subprocess.run(['sercomp']+ ["--mode=sexp"] + sc.serapi_args() + [fname], cwd=sc.cwd(),
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          encoding='utf8')
    if proc.returncode != 0:
        print('ERROR in sercomp', fname, file=log_file)
        print(proc.stderr, file=log_file)
    f = io.StringIO(initial_value=proc.stdout)
    return [safe_loc(sout) for sout in f]

def stm_list_of_vernac(fname: str, sc: SessionContext, log_file=sys.stderr):
    with open(fname,'rb') as fsrc:
        vernac_src = fsrc.read()
    loc_list = loc_list_of_vernac(fname, sc, log_file=log_file)
    return [vernac_src[bp:ep].decode('utf8') if (bp,ep) != (None,None) else 'SERCOMP_DECODE_ERROR' for (bp,ep) in loc_list]

def pycoq_exit(msg: str):
    print(msg)
    #os.sys.exit(1)
    return False



def process_add_response(rs, file=sys.stderr):
    if serapi_type(rs)=='Answer':
        print(serapi_type(rs), serapi_answer_entry(rs), serapi_answer_status(rs), file=file)
        if not serapi_answer_status(rs)  in ['Ack','Added','Completed']:
            print("ERROR: not expected response", resp, file=file)
            return None
        if serapi_answer_status(rs)=='Added':
            return serapi_added_entry(rs)
    elif serapi_type(rs)=='Feedback':
        return None
    else:
        raise Exception("Unknown serapi response")

def process_add_responses(presponses, log_file=sys.stderr):
    add_responses = [process_add_response(rs, file=log_file) for (rs,s) in presponses]
    add_responses = list(filter(lambda x: not x is None, add_responses))
    try:
        assert len(add_responses) == 1
        index = int(add_responses[0])
        print('added vernac statement to index {}'.format(index), file=log_file)
        return index
    except Exception as exc:
        print('vernac statement was not properly added', exc, file=log_file)
        print('received responses are', presponses, file=log_file)
        return None


def process_exec_responses(presponses, log_file=sys.stderr):
    for r,s in  presponses:
        #print(r.pretty())
        print(serapi_type(r), file=log_file)
        if serapi_type(r) == 'Answer':
            print(serapi_answer_entry(r), serapi_answer_status(r), file=log_file)
            if not serapi_answer_status(r) in ['Ack','Completed']:
                print('ERROR with answer_status {}'.format(serapi_answer_status(r)), file=log_file)
                return False
    return True
        

        


def process_vernac(job: SessionJob):
    fname = job.fname
    sc = job.sc
    debug = job.debug
#   print('Started processing {}'.format(job.fname))

    counter = 0

    with open(job.logfname,'w') if type(job.logfname)==str else job.logfname as log_file:
        print('Parsing vernac file {}'.format(fname), file=log_file)
        print('With session_context \n{}\n{}'.format(sc.cwd(),sc.serapi_args()), file=log_file)
        
        try:
            with CoqSession(sc, log_file=log_file) as coq:
                init_responses = list(coq.get_responses(timeout=5))
                print("Received {} initialization responses".format(len(init_responses)), file=log_file)
                
                vfile = stm_list_of_vernac(fname, sc, log_file=log_file) 
                print('Processing {} vernacular statements'.format(len(vfile)), file=log_file)
                total = len(vfile)
                for s in vfile:
                    print('Adding vernac {}: {}'.format(counter, ' '*30+ s), file=log_file)
                    coq.send_add(s)
                    presponses = coq.get_presponses(size=-1,timeout=30, finish_fun=completed_resp)
                    index = process_add_responses(presponses, log_file=log_file)
                    print('OK index {}'.format(index), file=log_file)

                    if not index is None:
                        print('Executing index {}'.format(index), file=log_file)
                        coq.execute(index)
                        presponses = coq.get_presponses(size=-1,timeout=30, finish_fun=completed_resp)
                        exec_result = process_exec_responses(presponses, log_file=log_file)
                        if exec_result:
                            print('Statement {} executed'.format(index), file=log_file)
                            print('The goals are', file=log_file)
                            for goal,s in coq.goals(index):
                                print(goal.pretty(), s, file=log_file)
                        else:
                            print('ERROR in execution', file=log_file)
                    else:
                        print('ERROR in adding', file=log_file)
                    counter += 1
                final_responses = list(coq.get_responses(timeout=5))
                print("Received {} final responses".format(len(final_responses)), file=log_file)
            print("FINISHED PARSING", file=log_file)
        except Exception as exc:
            print("ERROR in CoqSession because of", exc, file=log_file)
#   print('Finished  processing {}'.format(fname))

    return "Processed {} of {} statements from {}".format(counter, total, fname)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=(
                                     'Parse coq vernacular source by coq-serapi. '
                                     'If argument --file '
                                     'is missing assume stdin.'))
    parser.add_argument('--file','-f', metavar='file.v',type=str, help='process file.v')

    parser.add_argument('--ml-include-path','-I',metavar=('dir'),
                        action='append',
                        help='append filesystem to ML load path')

    parser.add_argument('--load-path','-Q',metavar=('dir','coqdir'),
                        nargs=2, action='append',
                        help='append filesystem dir mapped to coqdir to coq load path')

    parser.add_argument('--rec-load-path','-R',metavar=('dir','coqdir'),
                        nargs=2, action='append',
                        help='recursively append filesystem dir mapped '
                        'to coqdir to coq load path')
    

    parser.add_argument('--work-dir','-W', default=os.getcwd(),
                        metavar=('dir'),
                        help='work-dir. Default value is current dir')

    parser.add_argument('--sources','-s',metavar='sources.txt',
                        type=str, help='process all sources from the '
                        'list of sources in sources.txt. Not compatible '
                        'with --file option')

    parser.add_argument('--results','-r',metavar='results.txt',
                        type=str, help='save to the file results.txt')

    parser.add_argument('--completed','-C',action='store_true',
                        help='query serapi if add of vernac is completed')

    parser.add_argument('--exec','-E',action='store_false')

    parser.add_argument('--debug',type=int,default=3,help='debug level')

    parser.add_argument('--pool',default=1,type=int,help='number of pool workers')

    parser.add_argument('--process_all',action='store_true')

    parser.add_argument('--only-with-coqlog',action='store_true')

    parser.add_argument('--log-stderr',help='log output to stderr instead of .pycoqlog files',
                        action='store_true')
    
    
    args = parser.parse_args()


    if args.work_dir and not os.path.isdir(args.work_dir):
        pycoq_exit("Error: not found --work-dir {}".format(args.work_dir))


    if args.sources:
        sources = open(args.sources).readlines()
        print('Processing {} sources from the source list'.format(len(sources)))
    elif args.file and os.path.isdir(args.file):
        sources = list(find(args.file,VERNAC_FILE))
        if args.only_with_coqlog:
            sources = list(filter(lambda x: os.path.isfile(x+'.coqlog') or args.process_all, sources))
        print('Processing {} sources from the directory {}'.format(len(sources),args.file))
    elif args.file and os.path.isfile(args.file):
        sources = [args.file]
    else:
        print('No input sources are specified')
        sys.exit(-1)

    jobs = [SessionJob(fname,
                       session_context_from_args(args),
                       sys.stderr if args.log_stderr else fname+'.pycoqlog',
                       debug=args.debug) for fname in sources]
        
    with Pool(args.pool) as pool:
        lres=list(tqdm.tqdm(pool.imap(
            process_vernac, jobs, chunksize=1),total=len(sources),miniters=1))
    print('Processing finished')
    with open(args.results,'w') if args.results else sys.stdout as log_file:
        for e in lres:
            log_file.write(str(e)+'\n')

            
