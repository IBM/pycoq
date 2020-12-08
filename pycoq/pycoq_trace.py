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
import shutil
import sys

import pycoq.trace
from pycoq.pycoq_trace_config import EXECUTABLE, REGEX, DESCRIPTION


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

    pycoq.trace.strace_build(executable, args.regex, args.workdir, args.command)


if __name__ == '__main__':
    main()
