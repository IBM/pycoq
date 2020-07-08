from enum import Enum
from dataclasses import dataclass 
import sys
import numba
from numba import jit, jitclass

# reference parser of sexp

# parses string to sexp defined by grammar:
# sexp := ( term* )
# term := word | sexp
# word := sequence_of_non_special_characters | double_quoted_string_with_special_characters_backslash_escaped

# NOTICE: whitespace is necessary only to separate not quoted words from each other 

# Examples of valid sexp and their python representation
# ()            []
# (())          [[]]
# (()  ()  )    [[],[],[]]
# (abb()bcc)    ['abb',[],'bcc']
# (abb"bcc"())  ['abb','"bcc"',[]]


TOKEN_WORD = 0
TOKEN_OPEN_PAR = 1
TOKEN_CLOSE_PAR = 2

@numba.experimental.jitclass([('code',numba.types.int8),('value',numba.types.string)])
class Token():
    def __init__(self, code, value):
        self.code = code
        self.value = value
        

@jit(nopython=True) 
def skip_whitespace(s, pos):
    """ eats white space
    """
    while s[pos] == " ":
        pos += 1
    return pos
        
@jit(nopython=True)
def get_word(s, pos):
    """ eats next word or quoted string
    """
    if s[pos] == '"':
        pos += 1
        while pos < len(s) and s[pos] != '"':
            if s[pos] == '\\':
                if not (pos < len(s) - 1):
                    raise ValueError("Unfinished escape sequence")
                else:
                    pos += 2
            else:
                pos += 1
        if pos < len(s) and s[pos] == '"':
            return pos+1
        else:
            raise ValueError("Unfinished double quote")
    else:
        while pos < len(s) and (not s[pos] in ['"','(',')',' ']):
            pos += 1
        return pos

@jit(nopython=True)
def token_generator(s):
    """ generates tokens from string 
    """
    pos = 0
    while pos < len(s):
        while pos < len(s) and s[pos] == " ":
            pos += 1
        if pos == len(s):
            break
        if s[pos] == '(':
            yield Token(TOKEN_OPEN_PAR,'(')
            pos += 1
            continue
            
        elif s[pos] == ')':
            yield Token(TOKEN_CLOSE_PAR,')')
            pos += 1
            continue
        else:
            pos1 = get_word(s, pos)
            w = s[pos:pos1]
            if len(w) > 0:
                yield Token(TOKEN_WORD,w)
                pos = pos1
                continue
            else:
                raise Exception("Error in the parsing code: parser produced empty word, report bug")
    

        
def sexp_(t_gen):   
    """ returns sexpression from generator of tokens 
    """
    t = next(t_gen)            # if StopIteration indicates that OPEN_PAR was not closed before string ended 
    if t.code == TOKEN_WORD:
        return t.value
    elif t.code == TOKEN_OPEN_PAR:
        res = []
        while True:
            next_value = sexp_(t_gen)
            if next_value == None:
                break
            res.append(next_value)
        return res
    elif t.code == TOKEN_CLOSE_PAR:
        return None
    else:
        raise ValueError(f"Unexpected token {t} in sexp__")
        
        
        
def sexp(s):
    """ returns sexpression from string
    """
    g = token_generator(s)
    res = sexp_(g)
    if res == None:
        raise ValueError(f"Too many closing parentheses in trying to parse sexp")
    else:
        return res


if __name__ == '__main__':
    while True:
        s = sys.stdin.readline().strip()
        if s == "":
            break
        else:
            print(sexp(s))
 

