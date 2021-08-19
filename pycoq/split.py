''' splits input binary stream in utf8 encoding to coq statements 
    async readline from input binary stream 
'''

 
import io
import re
import os
import asyncio
import argparse

from typing import Iterable

import aiofile 


import pycoq.common
import pycoq.kernel



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
    '''
    [revised]
    '''
    return (pos > 0 and s[pos-1] == DOT)


def string_coq_stmts_pos(line, comment_level, in_string):
    '''
    [revised]
    '''
    res = []
    for m in separators.finditer(line):
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
            if not after_dot(line, m.start()):
                res.append(pos)
    return (res, comment_level, in_string)



def coq_stmts_of_lines(lines: Iterable[str]) -> Iterable[str]:
    '''
    [revised]
    converts iterable of lines to iterable of coq stmt 
    '''
    comment_level = 0
    in_string = False
    prefix = ""

    for line in lines:
        positions, comment_level, in_string = string_coq_stmts_pos(
            line, comment_level, in_string)
        start = 0
        for pos in positions:
            stmt = prefix + line[start:pos]
            prefix = ''
            start = pos
            yield stmt
        prefix = prefix + line[start:]


def coq_stmts_of_context(coq_ctxt: pycoq.common.CoqContext) -> Iterable[str]:
    '''
    [revised]
    returns generator of coq statements from a context
    '''
    source_filename = os.path.join(coq_ctxt.pwd, coq_ctxt.target)

    with open(source_filename, 'r') as fsource:
        for stmt in pycoq.split.coq_stmts_of_lines(fsource.readlines()):
            yield stmt


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

    
async def agen_coq_stmts(fin: asyncio.StreamReader, comment_level=0,
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

    print(len(parser_l))

    for (i, (a, b)) in enumerate(zip(parser_l)):
        if remove_comment(a) != b.strip():
            for pos in range(max(0, i-2), min(i+2, len(parser_l))):
                print("parser:")
                print(remove_comment(parser_l[pos]))

            break
            


if __name__ == "__main__":
    asyncio.run(main())


        
