'''interface with serlib.cparser module

We'll use platform defined C-types int (np.intc) and long long int
(np.ulonglong) for maximal portability because python C-api does not
support fixed width C types: https://docs.python.org/3/c-api/long.html
For numpy reference see
https://numpy.org/devdocs/user/basics.types.html

For platform reference see
https://en.cppreference.com/w/cpp/language/types

On 32 bit data model ILP32 (Win32, 32-bit Linux, OSX) and 64 bit
datamodel LP64 (Linux, OSX) and LLP64 (Windows):

int is 32 bit
long long is 64 bit


Py_ssize_t is signed integer of the same bitwidth as ssize_t 
Py_ssize_t seems to be equivalent to np.intp 
"Integer used for indexing, typically the same as ssize_t"
per https://numpy.org/devdocs/user/basics.types.html
'''
from typing import List
import numpy as np

import serlib.cparser


# buffer limit to exchange with C code to parse S-expression
# TODO: need to find how to determine BUFFER_SIZE_LIMIT dynamically
BUFFER_SIZE_LIMIT = 100000000



    

def hash_bytestring(bytestring: bytes) -> int:
    ''' interface to serlib.cparser.hash_string '''
    return serlib.cparser.hash_string(bytestring)

# TODO: REMOVE
# def list_of_string(input_s: str, parser=None) -> List[str]:
#     ''' from s-expression string "(expr_1 expr_2 ... expr_k)"
#     returns a list of strings ["expr_1", "expr_2", ..., "expr_k"]
#     '''
    
#     if parser is None:
#         p = SExpParser()
#     input_b = input_s.encode()
#     res, loc = p.postfix_of_bytestring(input_b), p.last_location()
#     n_args = -res[-1]
#     if not n_args >= 0:
#         raise ValueError("the input s-exprression {input_s} is not an s-expr list (may be an atom?)")
#     else:
#         args = []
#         for i in range(n_args):
#             _, loc = p.postfix_of_bytestring(input_b, [i]), p.last_location()
#             args.append(input_b[loc].decode())
#         return args


class SExpParser:
    ''' This class provides parsing functions for s-expressions. 

    A typical usage is to parse s-expressions obtained as goals
    from coq-serapi

    '''
    
    def __init__(self):
        # Load the shared library
        buffer_size = BUFFER_SIZE_LIMIT

        # Persistent dictionary
        self.hash_list = np.zeros(buffer_size, dtype=np.ulonglong)
        self.dict = {}
        self.inv_dict = [b'']
    
    def postfix_of_sexp(self, string, address=None):
        """
        return a postfix representation in np.array[int] of the input string
        containing the subtree s-expression at the address
        """
        return self.postfix_of_bytestring(string.encode('utf8'), address)

    def postfix_of_bytestring(self, bytestring, address=None):
        """
        return a postfix representation in np.array[int] of the input s-expression bytestring 
        at the tree address address
        //former parse_bytestring
        """
        if address is None:
            address = []
        np_address = np.array(address, dtype=np.intc)
        
        self._start_pos, self._end_pos, post_fix, np_add_dict = serlib.cparser.parse(
            bytestring,  np_address, self.hash_list, len(self.dict))

        for i in range(np_add_dict.shape[0]//2):
            start = np_add_dict[2*i]
            end = np_add_dict[2*i+1]
            word = bytestring[start:end]
            word_hash = hash_bytestring(word)
            self.hash_list[len(self.dict)] = word_hash
            self.dict[word] = len(self.dict)+1
            self.inv_dict.append(word)
        return post_fix

    def parse_bytestring_new(self, bytestring, address=[]):
        postfix = self.postfix_of_bytestring(bytestring, [])
        ann = serlib.cparser.annotate(postfix)
        start, end = serlib.cparser.subtree(postfix, ann, np.array(address, dtype=np.intc))
        return postfix[start:end]

    
    def last_location(self):
        return slice(self._start_pos, self._end_pos)

    def hash_dict(self):
        return {key: self.hash_list[value-1] for key,value in self.dict.items()}
    
    def to_sexp_legacy(self, encoding_list):
        stack = []
        for value in encoding_list:
            if value > 0:
                new_element = self.inv_dict[value]
            elif value == 0:
                new_element = b'()'
            else:
                new_element = b'(' + b' '.join(stack[value:]) + b')'
                del(stack[value:])
            stack.append(new_element)
        if stack:
            return stack[0].decode('utf8')
        else:
            return None
    
    def to_sexp(self, encoding_list):
        stack = []
        for value in encoding_list:
            if value > 0:
                new_element = self.inv_dict[value]
            elif value == 0:
                new_element = b'()'
            else:
                value_ = len(stack) + value
                new_element = b'(' + stack[value_]
                for element in stack[value_+1:]:
                    if not (new_element[-1] in [ord(')'), ord('"')] or element[0] in [ord('('), ord('"')]):
                        new_element += b' '
                    new_element += element
                new_element += b')'
                del(stack[value:])
            stack.append(new_element)
        if stack:
            return stack[0].decode('utf8')
        else:
            return None



    
    
def check_inverse(parser: SExpParser, bytestring: bytes) -> bool:
    encoding = parser.postfix_of_bytestring(bytestring)
    decoding = parser.to_sexp(encoding)
    reencoding = parser.postfix_of_bytestring(decoding)
    return (encoding == reencoding).all()



def encode(string, address):
    levels = len(address)
    open_pars = []
    output = []
    pos = 0
    while pos < len(string):
        if string[pos] == '(':
            open_pars.append(0)
            pos += 1
        elif string[pos] == ')':
            last_element = open_pars.pop()
            if open_pars[:levels] == address:
                output.append(-last_element)
            if open_pars:
                open_pars[-1] += 1
            pos += 1
        else:
            token = ''
            while pos < len(string) and string[pos] not in '()':
                token += string[pos]
                pos += 1
            print(token, open_pars)
            if open_pars[:levels] == address:
                output.append(token)
            open_pars[-1] += 1
    return output
