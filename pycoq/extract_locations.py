import argparse, sys

from lark_serapi import sexp_parser_mach as sexp_parser  # we define sexp parser there



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
    



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=('Extract locations from sexp file'))


    parser.add_argument('--file','-f',metavar='file.sexp',type=str, help='sexp file')
    args = parser.parse_args()

    with open(args.file,'r') if args.file != None else sys.stdin as vfile:
        for s in vfile:
            sexp = sexp_parser.parse(s.strip())
            print(*loc_of_sexp(sexp),sep=',')
