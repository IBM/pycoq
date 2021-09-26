'''
functions to work with opam
'''

from typing import Optional, List,  Tuple

import subprocess
import os
import asyncio

import pycoq.config
import pycoq.pycoq_trace_config
import pycoq.trace
import pycoq.log
import pycoq.split
import pycoq.serapi
import pycoq.query_goals


import serlib.parser


# refactor globals below to be loaded from a default config
# see e.g. https://tech.preferred.jp/en/blog/working-with-configuration-in-python/

MIN_OPAM_VERSION = "2."
DEFAULT_OCAML = "ocaml-variants.4.07.1+flambda"
COQ_REPO = "coq-released"
COQ_REPO_SOURCE = "https://coq.inria.fr/opam/released"
SWITCH_INSTALLED_ERROR = "[ERROR] There already is an installed switch named"
COQ_SERAPI = "coq-serapi"
#COQ_SERAPI_PIN = "8.13.0+0.13.0"
COQ_SERAPI_PIN = "8.11.0+0.11.1"
COQ_EXTRA_WARNING = ['-w', '-projection-no-head-constant',
             '-w', '-redundant-canonical-projection',
             '-w', '-notation-overridden',
             '-w', '-duplicate-clear',
             '-w', '-ambiguous-paths',
             '-w', '-undeclared-scope',
             '-w', '-non-reversible-notation']



def opam_version() -> Optional[str]:
    ''' returns opam version available on the system '''
    try:
        command = ['opam', '--version']
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        return res.stdout.decode().strip()
    except FileNotFoundError:
        pycoq.log.critical("opam not found")
        return None
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode} {error.stdout.decode()} {error.stderr.decode()}")
        return None

def opam_check() -> bool:
    ''' checks if opam version is at least MIN_OPAM_VERSION '''
    version = opam_version()
    pycoq.log.info(f"checked opam_version={version}")
    return version and version.startswith(MIN_OPAM_VERSION)
    # it would be nicer to use
    # pkg_resources.parse_version(version) >= pkg_resources.parse_version(MIN_OPAM_VERSION)
    # but ^^^ breaks for ~rc versions of opam

def root_option() -> List[str]:
    ''' constructs root option arg to call opam '''
    root = pycoq.config.opam_root()
    return ['--root', root] if not root is None else []

def opam_init_root() -> bool:
    ''' returns True if opam inititalizes root successfully '''
    if not opam_check():
        return False

    command = (['opam', 'init']
               + ['--disable-sandboxing']
               + root_option()
               + ['--bare', '-n'])
               
    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False


def opam_update() -> bool:
    '''
    returns True if opam update is successfull
    '''
    command = ( ['opam', 'update']  + root_option()
                + ['--all'] )

    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True

    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False

def opam_add_repo_coq() -> bool:
    ''' returns True if opam successfully adds coq repo '''
    if not opam_init_root():
        return False

    command = (['opam', 'repo'] + root_option()
               + ['--all-switches', 'add']
               + ['--set-default']
               + [COQ_REPO, COQ_REPO_SOURCE])

    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return opam_update()
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False


def opam_set_base(switch: str, compiler) -> bool:
    ''' set base package in the switch;
    the usage of this function is not clear
    '''
    command = (['opam', 'switch'] + root_option()
               + ['--switch', switch]
               + ['-y'] 
               + ['set-base', compiler])
    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False


def opam_install_package(switch: str, package: str) -> bool:
    ''' installs package into a selected switch or updates '''
    command = (['opam', 'install', '-y'] + root_option()
               + ['--switch', switch, package])
    pycoq.log.info(f"installing {package} in opam switch {switch} ...")
    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True

    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False

def opam_create_switch(switch: str, compiler: str) -> bool:
    ''' returns True if opam can create or recreate
    switch successfully '''

    if not opam_add_repo_coq():
        return False
    pycoq.log.info(f"soft (re)creating switch {switch} with compiler {compiler} in {root_option()[1]}")
    command = (['opam', 'switch'] + root_option()
               + ['--color', 'never']
               + ['create', switch, compiler])

    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True
    except subprocess.CalledProcessError as error:
        if (error.returncode == 2 and
            error.stderr.decode().strip().startswith(SWITCH_INSTALLED_ERROR)):
            pycoq.log.warning(f"opam: the switch {switch} already exists")

            return opam_install_package(switch, compiler)
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False
    


def opam_pin_package(coq_package: str,
                     coq_package_pin: str,
                     coq_serapi=COQ_SERAPI,
                     coq_serapi_pin=COQ_SERAPI_PIN,
                     compiler=DEFAULT_OCAML) -> bool:
    '''
    pins package to source in the switch
    '''
    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)
    pycoq.log.info(f"pinning package {coq_package} to pin {coq_package_pin} in switch {switch}")
    command = (['opam', 'pin', '-y']
               + root_option()
               + ['--switch', switch]
               + [coq_package, coq_package_pin])

    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return True
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return False


def opam_switch_name(compiler: str, coq_serapi: str,
                     coq_serapi_pin: str) -> str:
    ''' constructs switch name from compiler, coq_serapi and coq_serapi_pin '''
    
    return compiler + '_' + coq_serapi + '.' + coq_serapi_pin

def opam_install_serapi(coq_serapi=COQ_SERAPI,
                        coq_serapi_pin=COQ_SERAPI_PIN,
                        compiler=DEFAULT_OCAML) -> bool:
    ''' creates default switch and installs coq-serapi there
    '''

    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)
    if not opam_create_switch(switch, compiler):
        return False
    if not opam_pin_package(coq_serapi, coq_serapi_pin,
                            coq_serapi, coq_serapi_pin,
                            compiler):
        return False
    return opam_install_package(switch, coq_serapi)
                            



def opam_install_coq_package(coq_package: str,
                             coq_package_pin=None,
                             coq_serapi=COQ_SERAPI,
                             coq_serapi_pin=COQ_SERAPI_PIN,
                             compiler=DEFAULT_OCAML) -> bool:
    ''' installs coq-package into default switch
    name constructed from (compiler version)_(serapi version)
    '''
    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)

    if not opam_install_serapi(coq_serapi,
                               coq_serapi_pin,
                               compiler):
        return False

    if ((not coq_package_pin is None) and
        not opam_pin_package(coq_package, coq_package_pin, coq_serapi, coq_serapi_pin, compiler)):
        return False

    return opam_install_package(switch, coq_package)



def opam_default_root() -> Optional[str]:
    '''
    returns default root of opam
    '''
    if not opam_check():
        return False

    command = (['opam', 'config', 'var', 'root'])
    try:
        res = subprocess.run(command, check=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        log(res.stdout.decode(), res.stderr.decode())
        root = res.stdout.decode().strip()
        if os.path.isdir(root):
            return root
        else:
            pycoq.log.critical('missing opam default root directory {root}')
            return None
    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return None

    
def opam_executable(name: str, switch: str) -> Optional[str]:
    ''' returns coqc name in a given opam root and switch '''
    if not opam_check():
        return None
    command = (['opam', 'exec']
               + root_option()
               + ['--switch', switch]
               + ['--', 'which', name])
    try:
        res = subprocess.run(command, check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        ans = res.stdout.decode().strip()
        if not os.path.isfile(ans):
            pycoq.log.error(f"{name} obtained executing {command} "
                f"and resolved to {ans} was not found ")
            return None

        return ans

    except subprocess.CalledProcessError as error:
        pycoq.log.critical(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return None


def opam_strace_build(coq_package: str,
                      coq_package_pin = None,
                      coq_serapi=COQ_SERAPI,
                      coq_serapi_pin=COQ_SERAPI_PIN,
                      compiler=DEFAULT_OCAML) -> List[str]:
    ''' returns a list of pycoq context files 
    after opam build of a package; monitoring calls 
    with strace '''

    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)

    if not opam_create_switch(switch, compiler):
        return False

    if not opam_pin_package(coq_serapi, coq_serapi_pin, coq_serapi, coq_serapi_pin, compiler):
        return False

    if not opam_install_package(switch, coq_serapi):
        return False

    if ((not coq_package_pin is None) and
        not opam_pin_package(coq_package, coq_package_pin, coq_serapi, coq_serapi_pin, compiler)):
        return False

    executable = opam_executable('coqc', switch)
    if executable is None:
        pycoq.log.critical("coqc executable is not found in {switch}")
        return []

    regex = pycoq.pycoq_trace_config.REGEX

    workdir = None

    command = ( ['opam', 'reinstall']
                + root_option()
                + ['--yes']
                + ['--switch', switch]
                + ['--keep-build-dir']
                + [coq_package] )

    pycoq.log.info(f"{executable}, {regex}, {workdir}, {command}")

    strace_logdir = pycoq.config.strace_logdir()
    return pycoq.trace.strace_build(executable, regex, workdir, command, strace_logdir)


def opam_strace_command(command: List[str],
                        workdir: str,
                      coq_serapi=COQ_SERAPI,
                      coq_serapi_pin=COQ_SERAPI_PIN,
                      compiler=DEFAULT_OCAML) -> List[str]:
    ''' strace command
    '''

    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)
    root = pycoq.config.opam_root()
    if root is None:
        root = opam_default_root()

    if root is None:
        pycoq.log.critical("in opam_strace_build failed to determine opam root")
        return []

    executable = opam_executable('coqc', switch)
    if executable is None:
        pycoq.log.critical("coqc executable is not found")
        return []

    regex = pycoq.pycoq_trace_config.REGEX

    pycoq.log.info(f"{executable}, {regex}, {workdir}, {command}")

    return pycoq.trace.strace_build(executable, regex, workdir, command)


def opam_coqtop(coq_ctxt: pycoq.common.CoqContext,
              coq_serapi=COQ_SERAPI,
              coq_serapi_pin=COQ_SERAPI_PIN,
              compiler=DEFAULT_OCAML) -> int:

    '''
    runs coqtop with a given pycoq_context
    returns error code of coqtop with Coqtop Exit on Error flag
    '''
    iqr_args = pycoq.common.coqc_args(coq_ctxt.IQR())
    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)

    command = (['opam', 'exec']
               + root_option()
               + ['--switch', switch]
               + ['--', 'coqtop']
               + ['-q']
               + iqr_args
               + ['-set', 'Coqtop Exit On Error']
               + ['-topfile', coq_ctxt.target]
               + ['-batch', '-l', coq_ctxt.target])
    pycoq.log.info(f"{' '.join(command)} on {coq_ctxt.target}")
    try:
        res = subprocess.run(command,
                             cwd=coq_ctxt.pwd,
                             check=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        pycoq.log.info(f"{command}: {res.stdout.decode()} {res.stderr.decode()}")
        return 0
    except subprocess.CalledProcessError as error:
        pycoq.log.error(f"{command} returned {error.returncode}: {error.stdout.decode()} {error.stderr.decode()}")
        return error.returncode

async def opam_coqtop_stmts(coq_ctxt: pycoq.common.CoqContext,
                       coq_serapi=COQ_SERAPI,
                       coq_serapi_pin=COQ_SERAPI_PIN,
                       compiler=DEFAULT_OCAML) -> List[str]:
    '''
    feeds coqtop repls with a stream
    of coq staments derived from coq_context_fname

    returns a list of pairs: <input, output>
    '''
    print("entered opam_coqtop_stmts")

    iqr_args = pycoq.common.coqc_args(coq_ctxt.IQR())
    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)
    command = (['opam', 'exec']
              + root_option()
              + ['--switch', switch]
              + ['--', 'coqtop']
              + ['-q']
              + iqr_args
              + ['-set', 'Coqtop Exit On Error']
              + ['-topfile', coq_ctxt.target])

    pycoq.log.info(f"interactive {' '.join(command)}")

    ans = []
    proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            cwd=coq_ctxt.pwd)
    print(f"proc {proc} is created")

    for stmt in pycoq.split.coq_stmts_of_context(coq_ctxt):
        print(f"writing {stmt}")
        proc.stdin.write(stmt.encode())
        print("waiting for drain")
        await proc.stdin.drain()
    proc.stdin.write_eof()


    while True:
        line = (await proc.stdout.readline()).decode()
        if line == '':
            break
        ans.append(line)
        print(f"response {line}")

    err = (await proc.stderr.read()).decode()
    print(f"error {err}")
    
    return ans, err, proc.returncode


def opam_serapi_cfg(coq_ctxt: pycoq.common.CoqContext=None,
                    coq_serapi=COQ_SERAPI,
                    coq_serapi_pin=COQ_SERAPI_PIN,
                    compiler=DEFAULT_OCAML,
                    debug=False) -> List[Tuple[str]]:
    ''' returns serapi cfg from coq_ctxt '''
    if coq_ctxt == None:
        coq_ctxt = pycoq.common.CoqContext(pwd=os.getcwd(),
                                           executable='',
                                           target='default_shell')

    iqr_args = pycoq.common.serapi_args(coq_ctxt.IQR())
    switch = opam_switch_name(compiler, coq_serapi, coq_serapi_pin)
    debug_option = ['--debug'] if debug else []

    command = (['opam', 'exec']
              + root_option()
              + ['--switch', switch]
              + ['--', 'sertop']
              + iqr_args
              + ['--topfile', coq_ctxt.target]
              + debug_option)

    return pycoq.common.LocalKernelConfig(command=command,
                                         env=None,
                                         pwd=coq_ctxt.pwd)



def log_query_goals_error(_serapi_goals, serapi_goals, serapi_goals_legacy):
    dumpname = 'pycoq_opam_serapi_query_goals.dump'
    pycoq.log.info(f"ERROR discrepancy in serapi_goals\n"
                   f"source: {_serapi_goals}\n"
                   f"serapi_goals: {serapi_goals}\n"
                   f"serapi_goals_legacy: {serapi_goals_legacy}\n"
                   f"input source dumped into {dumpname}\n")
    open(dumpname,'w').write(_serapi_goals)
    raise ValueError("ERROR serapi_goals discrepancy")


async def opam_coq_serapi_query_goals(coq_ctxt: pycoq.common.CoqContext,
                                      coq_serapi=COQ_SERAPI,
                                      coq_serapi_pin=COQ_SERAPI_PIN,
                                      compiler=DEFAULT_OCAML,
                                      debug=False) -> List[Tuple[str]]:
    '''
    returns SerapiGoals object
    after each execution of Coq Command
    '''
    cfg = opam_serapi_cfg(coq_ctxt, coq_serapi, coq_serapi_pin,
                          compiler, debug)

    logfname = pycoq.common.serapi_log_fname(
        os.path.join(coq_ctxt.pwd, coq_ctxt.target))

    res = []

    # par = serlib.parser.SExpParser()
    
    async with pycoq.serapi.CoqSerapi(cfg, logfname=logfname) as coq:
        for stmt in pycoq.split.coq_stmts_of_context(coq_ctxt):
            _, _, coq_exc, _ = await coq.execute(stmt)
            if coq_exc:
                break

            _serapi_goals = await coq.query_goals_completed()
            
            post_fix = coq.parser.postfix_of_sexp(_serapi_goals)
            ann = serlib.cparser.annotate(post_fix)

            serapi_goals = pycoq.query_goals.parse_serapi_goals(coq.parser, post_fix, ann, pycoq.query_goals.SExpr)
            
            res.append((stmt, _serapi_goals, serapi_goals))
    return res
