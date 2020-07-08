# -*- coding: utf-8 -*-
r""" Execute process and trace system execve calls of a specified executable 
whose single argument matches a specified python regex string. Record
the arguments and the environment for each matching system call
to the file with the same name as argument extended
by suffix common.CONTEXT_EXT


  Example:

pycoq-trace --workdir tests/data/CompCert --executable coqc --regex 'v$' make

  TODO:
    * possible bug: check hex and dehex functions vs strace interface on "\xa" versus "\x0a" ?
    * expose defaults in config
    * expose module functionality as a python function
    * consider the case of multiple arguments matching regex
    * consider regex for executable instead of exact matche

"""

import argparse
import os
import sys
import subprocess
import tempfile
import re 
import ast
import shutil

from typing import List, Dict
from functools import lru_cache

from dataclasses import dataclass, field

from strace_parser.json_transformer import to_json
from strace_parser.parser import get_parser


from pycoq.common import CoqContext, context_fname, dump_context
from pycoq.pycoq_trace_config import EXECUTABLE, REGEX, DESCRIPTION


@dataclass
class ProcContext():
    executable: str = ''
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)


def hex_rep(b):
    if isinstance(b, str):
        return "".join(['\\' + hex(c)[1:]  for c in b.encode('utf8')])
    else:
        raise ValueError('in hex_rep on ' + str(b))

def dehex_str(s):
    if len(s) > 2 and s[0] == '"' and s[-1] =='"':
        try:
            temp = 'b' + s
            return ast.literal_eval(temp).decode('utf8')
        except Exception as exc:
            print("pycoq: ERROR DECODING", temp)
            raise exc
    else:
        return s
            

def dehex(d):
    if isinstance(d, str):
        return dehex_str(d)
    elif isinstance(d, list):
        return [dehex(e) for e in d]
    elif isinstance(d, dict):
        return {k:dehex(v) for k, v in d.items()}
    

def simplify(d):
    if isinstance(d, str):
        return d
    elif isinstance(d, list):
        return [simplify(e) for e in d]
    elif isinstance(d, dict):
        if d.keys() == {'type', 'value'} and d['type'] == 'other' or d['type'] == 'bracketed':
            return simplify(d['value'])
        else:
            return {simplify(k) : simplify(v) for k, v in d.items()}

            

def parse_strace_line(parser, line):
    line_tree = parser.parse(line)
    line_json = to_json(line_tree)
    assert isinstance(line_json, list)
    assert len(line_json) == 1
    d = line_json[0]
    if d['type'] == 'syscall' and d['name'] == 'execve':
        dargs = d['args']
        return simplify(dehex(dargs))

def dict_of_list(l, split='='):
    d = {}
    for e in l:
        assert isinstance(e, str)
        pos = e.find(split)
        assert pos > 0
        d[e[:pos]]  = e[pos+1:]
    return d

@lru_cache
def cpattern(regex):
    return re.compile(regex)

def target_files(args, regex):
    for s in args:
        if not cpattern(regex).fullmatch(s) is None:
            yield s

    


def record_context(line, parser, regex):
    record = parse_strace_line(parser, line)
    p_context = ProcContext(executable=record[0], args=record[1], env=dict_of_list(record[2]))
    t_files = list(target_files(p_context.args, regex))
    if len(t_files) == 0:
        return None
    elif len(t_files) == 1:
        pwd = p_context.env['PWD']
        target = t_files.pop()
        cc = CoqContext(pwd=pwd, 
                        executable=p_context.executable,
                        target=target,
                        args=p_context.args,
                        env=p_context.env)
        target_fname = os.path.join(pwd, target)
        return dump_context(context_fname(target_fname), cc)
    else:
        print(f"pycoq: WARNING: recording context coqc on a list "
              f"of target files matching {regex} is not implemented" 
              f"the list of targets is {t_files}")
        return 0

        
def parse_strace_logdir(logdir, executable, regex):
    print(f'pycoq: parsing strace log filtered by execve({executable}) with a single argument matching {regex}')
    parser = get_parser()
    for logfname_pid in os.listdir(logdir):
        with open(os.path.join(logdir,logfname_pid),'r') as log:
            for line in iter(log.readline, ''):
                if line.find(hex_rep(executable)) != -1:
                    record_context(line, parser, regex)

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--executable', type=str,
                        help='monitor calls to executable', default=EXECUTABLE)

    parser.add_argument('--regex', type=str, help='pattern as python regex string '
                        '(hint: be careful not to mess up with shell expasion '
                        'when passing string as an argument )', default=REGEX)
    
    parser.add_argument('--workdir', type=str,
                        help='run ...  in work directory', default=os.getcwd())
    parser.add_argument('command', metavar='...', help='command to run', nargs=argparse.REMAINDER)


    args = parser.parse_args()

    executable = shutil.which(args.executable)

    if executable is None:
        parser.print_help()
        print(f'Error: executable {args.executable} is not found in the system path.\n'
              f'Hint: if {args.executable} is installed in opam, '
              'do not forget to activate opam environment by:\n'
              'opam switch <opam-coq-environment>\n'
              'eval $(opam env)')
        sys.exit(-1)
    else:
        executable = os.path.abspath(executable)

    if len(args.command) == 0:
        parser.print_help()
        print('Error: command is empty')
        sys.exit(-1)

    with tempfile.TemporaryDirectory() as logdir:
        logfname = os.path.join(logdir, 'strace.log')
        print(f'pycoq: monitoring system calls of {executable}')
        print("pycoq: executing strace -o {}".format(logfname),
              args.command, "in workdir", args.workdir)
        with subprocess.Popen(['strace', '-e', 'trace=execve',
                               '-v','-ff','-s', '100000000',
                               '-xx','-ttt',
                               '-o', logfname] + args.command,
                              cwd=args.workdir,
                              text=True,
                              bufsize=1,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            for line in iter(proc.stdout.readline,''):
                print("stdout: {}".format(line), end='')
            err = proc.stderr.read()
            print("stderr:")
            print(err, end='')
            print('pycoq: waiting for command to finish...')
            proc.wait()
        print('pycoq: command finished')
        parse_strace_logdir(logdir, executable, args.regex)



if __name__ == '__main__':
    main()
