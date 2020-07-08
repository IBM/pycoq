''' interface with serlib.cparser module

We'll use platform defined C-types int (np.intc) and long long int (np.ulonglong) for maximal portability because python C-api does not support fixed width C types:  https://docs.python.org/3/c-api/long.html
For numpy reference see https://numpy.org/devdocs/user/basics.types.html

For platform reference see https://en.cppreference.com/w/cpp/language/types

On 32 bit data model ILP32 (Win32, 32-bit Linux, OSX) and 64 bit datamodel LP64 (Linux, OSX) and LLP64 (Windows):

int is 32 bit
long long is 64 bit
'''


import serlib.cparser
import numpy as np
import random

class SExpParser:
    def __init__(self):
        # Load the shared library
        buffer_size=20000000
        

        self.output_buffer = np.zeros(buffer_size, dtype=np.intc)
        self.add_dict_buffer = np.zeros(buffer_size, dtype=np.intc)
        self.hash_list = np.zeros(buffer_size, dtype=np.ulonglong)
        
        # Persistent dictionary
        self.dict = {}
        self.inv_dict = [b'']
        
    def hash_bytestring(self, bytestring):
        return serlib.cparser.hash_string(bytestring)
    
    def parse_string(self, string, address=[]):
        return self.parse_bytestring(string.encode('utf8'), address)
    
    def parse_bytestring(self, bytestring, address=[]):
        address_buffer = np.array(address, dtype=np.intc)
        
        num_outputs, add_dict_size = serlib.cparser.parse(bytestring, address_buffer, self.hash_list, 
                                    len(self.dict),
                                    self.output_buffer, self.add_dict_buffer)
        #num_outputs, add_dict_size = result//(2**32), result%(2**32)
        #print(num_outputs, add_dict_size)
        #print(self.output_buffer[:20])
        for i in range(add_dict_size):
            start = self.add_dict_buffer[2*i]
            end = self.add_dict_buffer[2*i+1]
            word = bytestring[start:end]
            word_hash = self.hash_bytestring(word)
            self.hash_list[len(self.dict)] = word_hash
            self.dict[word] = len(self.dict)+1
            self.inv_dict.append(word)
        return self.output_buffer[:num_outputs].copy()

    def hash_dict(self):
        return {key: self.hash_list[value-1] for key,value in self.dict.items()}
    
    def to_sexp(self, encoding_list):
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
    
    def goal(self, bytestring, goal_id):
        return self.to_sexp(self.parse_bytestring(bytestring, address=[1,0,1,0,1,goal_id,1,1]))
    
    def hyp(self, bytestring, goal_id):
        return self.to_sexp(self.parse_bytestring(bytestring, address=[1,0,1,0,1,goal_id,2,1]))
    
    
def check_inverse(parser, bytestring):
    encoding = parser.parse_bytestring(bytestring)
    decoding = parser.to_sexp(encoding)
    reencoding = parser.parse_bytestring(decoding)
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
            if open_pars[:levels] == address: output.append(-last_element)
            if open_pars: open_pars[-1] += 1
            pos += 1
        else:
            token = ''
            while pos < len(string) and string[pos] not in '()':
                token += string[pos]
                pos += 1
            print(token, open_pars)
            if open_pars[:levels] == address: output.append(token)
            open_pars[-1] += 1
    return output
