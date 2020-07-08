''' splits input binary stream in utf8 encoding to coq statements 

    async readline from input binary stream 
  
    after removing comments we observe difference on 
      python pycoq/split.py tests/data/CompCert/lib/Zbits.v  
 
    sercomp parses the following line
    - rewrite two_power_nat_O. 
    as two separate coq statements 
'''

 
import io
import re
import aiofile 
import asyncio
import argparse
import os
import sys
import time


import pycoq.common
import pycoq.kernel


async def coq_stmts(inp: io.BufferedReader, sep='\n'):
    prefix = ""
    while True:
        line = inp.readline()
        if not line:
            break
        chunks = line.split(sep=sep)
        chunks[0] = prefix + chunks[0]
        prefix = chunks[-1]
        for chunk in chunks[:-1]:
            yield chunk + sep

DOT = r'.'
QUOTE = r'"'
DOTWHITE = r'\.\s+'
COMMENTSTART = r'\(\*'
COMMENTFINISH = r'\*\)'

SEPARATORS = (
    '(?P<quote>' + QUOTE + ')|'
    '(?P<dotwhite>' + DOTWHITE + ')|'
    '(?P<commentstart>' + COMMENTSTART + ')|'
    '(?P<commentfinish>' + COMMENTFINISH + ')')
    
separators = re.compile(SEPARATORS)

def after_dot(s, pos):
    return (pos > 0 and s[pos-1] == DOT)


def string_coq_stmts_pos(s, comment_level, in_string):
    res = []
    for m in separators.finditer(s):
        sep = m.lastgroup
        pos = m.end()
        if sep == 'quote':
            in_string = not in_string
        elif sep == 'commentstart':
            if not in_string:
                comment_level += 1
            else:
                pass
        elif sep == 'commentfinish':
            if not in_string:
                if comment_level > 0:
                    comment_level -= 1
                else:
                    pass
            else:
                pass
        elif (sep == 'dotwhite'
              and not in_string
              and comment_level == 0):
            if not after_dot(s, m.start()):
                res.append(pos)
    return (res, comment_level, in_string)


def remove_comment(s: str):
    res = []
    start = 0
    in_string = False
    comment_level = 0
    for m in separators.finditer(s):
        sep = m.lastgroup

        if sep == 'quote':
            in_string = not in_string
        elif sep == 'commentstart':
            if not in_string:
                if comment_level == 0:
                    if m.start() > start:
                        res.append( s[start:m.start()] )   # insert another whitespace instead of comment
                comment_level += 1
            else:
                pass
        elif sep == 'commentfinish':
            if not in_string:
                if comment_level > 0:
                    comment_level -= 1
                    if comment_level == 0:
                        start = m.end()
                else:
                    print('WARNING:  *) not matching (*')
            else:
                pass
        elif (sep == 'dotwhite'
              and not in_string
              and comment_level == 0):
            pass

    res.append(s[start:])

    return " ".join([x.strip() for x in res]).strip()

    
async def agen_coq_stmts(fin: asyncio.StreamReader , comment_level=0,
                        in_string=False, prefix=''):
    """ 
    takes binary stream as input
    yields coq statements in utf8 string as output
    """
    while True:
        bline = await fin.readline()
        line = bline.decode('utf8')
        if line == '':
            break
        positions, comment_level, in_string = string_coq_stmts_pos(
            line, comment_level, in_string)
        start = 0
        for pos in positions:
            stmt = prefix + line[start:pos]
            prefix = ''
            start = pos 
            yield stmt
        prefix = prefix + line[start:]


# begin compare with sercomp 
from pycoq.lark_serapi import sexp_parser_mach as sexp_parser

def loc_of_sexp(sexp):
    l =  [[str(x) for x in
     sexp.children[0].children[1].children[1].children[0].children[i].children] for i in range(5,7)]
    bp, ep = l[0], l[1]
    if not(bp[0]=='bp' and ep[0]=='ep'):
        raise Exception('Unexpected format of location bp {} ep {}'.format(bp, ep))
    else:
        try:
            iloc = int(bp[1]), int(ep[1])
        except:
            raise Exception('Unexpected format of location bp {} ep {}'.format(bp, ep))
        
        return iloc


def safe_loc(sout):
    try: 
        p = loc_of_sexp(sexp_parser.parse(sout.strip()))
    except Exception:
        p = (None,None)
    return p


# def loc_list_of_vernac(fname: str, sc: SessionContext, log_file=sys.stderr):
#     proc = subprocess.run(['sercomp']+ ["--mode=sexp"] + sc.serapi_args() + [fname], cwd=sc.cwd(),
#                                           stdin=subprocess.PIPE,
#                                           stdout=subprocess.PIPE,
#                                           stderr=subprocess.PIPE,
#                                           encoding='utf8')
#     if proc.returncode != 0:
#         print('ERROR in sercomp', fname, file=log_file)
#         print(proc.stderr, file=log_file)
#     f = io.StringIO(initial_value=proc.stdout)
#     return [safe_loc(sout) for sout in f]


async def loc_list_of_vernac(source: str):
    coq_ctxt = pycoq.common.load_context(pycoq.common.context_fname(source),
                                         quiet=True)
    ser_args = pycoq.common.serapi_args(coq_ctxt.IQR())
    pwd = coq_ctxt.pwd
    ser_args = ['--mode=sexp'] + ser_args + [source]

    with open(source,'rb') as bsource:
        source_btxt = bsource.read()
    
    print('ser_args', ser_args)
    cfg = pycoq.common.serapi_kernel_config(kernel='sercomp',
                                            args=ser_args,
                                            pwd=pwd)
    try:
        async with pycoq.kernel.LocalKernel(cfg) as sercomp:
            print('started sercomp')
            async for line in sercomp.readlines(timeout=10):
                start, fin = safe_loc(line)
                yield source_btxt[start:fin].decode('utf8')

            async for line in sercomp.readlines_err(timeout=10):
                print(line)
            
    except FileNotFoundError:
        print('failed to start sercomp')
                                            
# finish compare with sercomp

async def run_parser(source: str):
    async with aiofile.AIOFile(source, 'rb') as fin:
        stream = aiofile.LineReader(fin)
        in_string = False
        comment_level = 0
        async for stmt in agen_coq_stmts(stream, comment_level, in_string):
            yield stmt




async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='source .v coq file')
    args = parser.parse_args()
    source = os.path.abspath(args.source)

    parser_l = []
    async for s in run_parser(source):
        parser_l.append(s)

    sercomp_l = []
    async for s in loc_list_of_vernac(source):
        sercomp_l.append(s)

    print(len(parser_l), len(sercomp_l))

    for (i, (a, b)) in enumerate(zip(parser_l, sercomp_l)):
        if remove_comment(a) != b.strip():
            for pos in range(max(0, i-2), min(i+2, len(parser_l), len(sercomp_l))):
                print("parser:")
                print(remove_comment(parser_l[pos]))

                print("sercomp:")
                print(sercomp_l[pos].strip())
            break
            


if __name__ == "__main__":
    asyncio.run(main())


        
