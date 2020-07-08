# https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md
from lark import Lark
import lark 

#ATOM: /[^()\s]+/ matches any character except () and whitespace
#ATOMS : /\"(\\.|[^\"\\])*\"/   # escaped ocaml string enclosed in double quotes, accept the string as a sequence of (backslash_any_character or any_character_except_quote_or_backslash) enclosed between double quotes 

sexp_parser_mach = Lark(
    r"""
   sexp : ATOM | list 
    list : "(" ( ATOMS|list|ATOM (" " ATOM)* )* ")"
    ATOM : /[∅∪∩≡⊆∈\w\.\/\-\#\[\]\,\>\<\'\*\?\=\|\@\+\:\^\`\{\}\&\~\%\!]+/
    ATOMS : /\"(\\.|[^\"\\])*\"/
    """, start='sexp', parser="lalr", keep_all_tokens=False)


sexp_parser_human = Lark(r"""
   sexp  : list  | ATOM
   list : "(" [sexp ( (" "|"\n"|"\t")+ sexp)*] ")"
   ATOM : /[A-Za-z0-9_\.\/\-]+/
   """, start='sexp', parser="lalr", keep_all_tokens=False)

json_parser = Lark(r"""
    value: dict
         | list
         | ESCAPED_STRING
         | SIGNED_NUMBER
         | "true" | "false" | "null"

    list : "[" [value ("," value)*] "]"

    dict : "{" [pair ("," pair)*] "}"
    pair : ESCAPED_STRING ":" value

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """, start='value')



def left_value(rs):
    if type(rs)==lark.tree.Tree:
        return left_value(rs.children[0])
    else:
        return rs.value


def serapi_type(p):
    return p.children[0].children[0].value

def serapi_answer_entry(p):
    return int(p.children[0].children[1].value)
    
def serapi_answer_status(p):
    return left_value(p.children[0].children[2])


def serapi_added_entry(p):
    return p.children[0].children[2].children[1].value
            

def ocaml_string_quote(s):
    return s.replace('\\','\\\\').replace('\"','\\\"')



if __name__ == "__main__":
    string_json = '{"key": ["item0", "item1", 3.14]}'    
    print(json_parser.parse(string_json).pretty())

    string_serapi = "(Feedback((doc_id 0)(span_id 0)(route 0)(contents(FileLoaded Coq.Init.Prelude coq-serapi/lib/coq/theories/Init/Prelude.vo))))"
    print(sexp_parser_mach.parse(string_serapi).pretty())
    

    with open('test_out.txt','w') as tout:
        for s in open('test_in.txt','r'):
            tout.write(ocaml_string_quote(s))

    
    
