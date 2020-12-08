import os, sys

import re


from utils import find, VERNAC_FILE, args_from_coqlog

def process1(rootdir):
    for d in sorted(os.listdir(rootdir)):
        cp_file = os.path.isfile(os.path.join(rootdir,d,'_CoqProject'))
        make_file = os.path.isfile(os.path.join(rootdir,d,'Make'))
        c_file = os.path.isfile(os.path.join(rootdir,d,'configure'))
        if not (cp_file != make_file):
            print(d, cp_file, make_file, c_file)

def process_all(vfiles):
    for x in list(filter(lambda x: os.path.isfile(x+'.coqlog'),vfiles)):
        a = args_from_coqlog(x)

vfiles=find('/home/pestun/code/clones/CoqGym/coq_projects',VERNAC_FILE)

process_all(vfiles)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=(
        'explore directory with coq-project'))

    parser.print_help()

    parser.add_argument('--dir',metavar='project-dir',type=str,
                        help='coq-projects dir', default='/home/pestun/code/CoqGym/coq_projects')

                        

    process(arg.dir)

    
    
