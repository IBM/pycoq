import re
import os
import shlex
import argparse

VERNAC_FILE = ".*\.v$"


def quote(s):
    return('"'+s+'"')


class SessionJob():
    def __init__(self,fname,default_sc,logfname,debug=0):
        self.fname=fname
        self.sc=default_sc
        if os.path.isfile(fname+'.coqlog'):
            self.sc = session_context_from_coqlog(fname)
        self.logfname=logfname
        self.debug = debug



class SessionContext():
    ''' populate CoqContext with
    args.cwd                  #command workdir
    args.ml_include_path      
    args.load_path
    args.rec_load_path'''

    def __init__(self, cwd=os.getcwd(), ml_include_path=[], load_path=[], rec_load_path=[]):
        listify  = lambda x: [] if x is None else x 
        self._cwd = cwd
        self._ml_include_path =  listify(ml_include_path)
        self._load_path = listify(load_path)
        self._rec_load_path = listify(rec_load_path)

        

    def cwd(self):
        return self._cwd

    def serapi_args(self):
        return ( ["-I{}".format(a) for a in self._ml_include_path] +
                 ["-Q{},{}".format(a,b) for (a,b) in self._load_path] + 
                 ["-R{},{}".format(a,b) for (a,b) in self._rec_load_path] 
                )

def session_context_from_args(default_args):
    return SessionContext(cwd=default_args.work_dir,
                            ml_include_path = default_args.ml_include_path,
                            load_path = default_args.load_path,
                            rec_load_path = default_args.rec_load_path)


def session_context_from_coqlog(x):
    with open(x+'.coqlog') as f:
        cwdline = f.readline()
        argline = f.readline()
    arglist = shlex.split(argline)
    arglist = [quote(arglist[i]) if i>=1 and arglist[i-1]=='-w' else arglist[i] for i in range(len(arglist))]


    parser = argparse.ArgumentParser()
    #parser = OptionParser()
    parser.add_argument('-q',action='store_true')
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

    parser.add_argument('-w',action='append',nargs=1,type=str)

    parser.add_argument('-dump-glob',action='append',nargs=1,type=str)

    parser.add_argument('source',type=str,nargs=1)

    args=parser.parse_args(arglist)

    return SessionContext(cwd = cwdline.strip(),
                        ml_include_path = args.ml_include_path,
                        load_path = args.load_path,
                        rec_load_path = args.rec_load_path)
    


    



def find(rootdir, pattern):
    regex = re.compile(pattern)
    for root, dirs, files in os.walk(rootdir):
        for name in files:
            if regex.match(name):
                yield(os.path.abspath(os.path.join(root,name)))
