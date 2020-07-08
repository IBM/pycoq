import os
import argparse
import shutil
import re

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import List, Dict
from pycoq.pycoq_trace_config import CONTEXT_EXT

TIMEOUT_TERMINATE = 5

_DEFAULT_SERAPI_LOGEXT = "._pycoq_serapi"



@dataclass
class IQR():
    I = List[str]             
    Q = List[List[str]]       # List of pairs of str
    R = List[List[str]]       # List of pairs of str


@dataclass_json
@dataclass
class CoqContext:
    pwd: str
    executable: str
    target: str
    args: List[str] = field(default_factory=list)
    env: Dict[str,str] = field(default_factory=dict)

    def IQR(self) -> IQR:
        parser = argparse.ArgumentParser()
        parser.add_argument('-I', metavar=('dir'),
                            nargs=1,
                            action='append',
                            help='append filesystem to ML load path')

        parser.add_argument('-Q', metavar=('dir', 'coqdir'),
                            nargs=2, action='append',
                            help='append filesystem dir mapped to coqdir to coq load path')

        parser.add_argument('-R', metavar=('dir', 'coqdir'),
                            nargs=2, action='append',
                            help='recursively append filesystem dir mapped '
                            'to coqdir to coq load path')
        args, _ = parser.parse_known_args(self.args)
        return args


@dataclass
class LocalKernelConfig():
    executable: str = ''
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    pwd: str = os.getcwd()


@dataclass
class RemoteKernelConfig():
    hostname: str
    port: int


def context_fname(target_fname):
    return target_fname + CONTEXT_EXT

def dump_context(fname: str, cc: CoqContext):
    with open(fname, 'w') as f:
        print('pycoq: recording context to', fname)
        f.write(cc.to_json())
    
def load_context(fname: str, quiet=False):
    """
    loads CoqContext from pycoq_strace log file 
    if file is missing and quiet=True falls to default CoqContext
    """
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            return CoqContext.from_json(f.read())
    elif quiet:
        return CoqContext(pwd=os.getcwd(), executable='', target='')
    else:
        raise FileNotFoundError



def serapi_args(args: IQR) -> List[str]:
    res = []
    if args.I:
        for x in args.I:
            res += ['-I', ','.join(x)]

    if args.Q:
        for x in args.Q:
            res += ['-Q', ','.join(x)]

    if args.R:
        for x in args.R:
            res += ['-R', ','.join(x)]
    return res

    


def serapi_kernel_config(kernel='sertop', opam_switch='pycoq', args=None, pwd=os.getcwd(), remote=False, ):
    assert remote == False # support for remote kernel not yet implemented 
    if opam_switch is None:
        env = os.environ
        return LocalKernelConfig(executable=kernel, args=args, env=os.environ(), pwd=pwd)
    else:
        executable = 'opam'
        args_prefix = ['exec', '--switch',  opam_switch, '--', kernel]
        args = args_prefix if args is None else args_prefix + args
        env = {'HOME': os.environ['HOME']}
        return LocalKernelConfig(executable=executable, args=args, env=env, pwd=pwd)
        

def find_files(rootdir, pattern):
    regex = re.compile(pattern)
    for root, dirs, files in os.walk(rootdir):
        for name in files:
            if regex.match(name):
                yield(os.path.abspath(os.path.join(root,name)))

