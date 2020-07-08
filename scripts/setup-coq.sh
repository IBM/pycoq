#!/bin/bash

MINOPAMVERSION=2.0.0

export MAKEFLAGS=-j$(nproc)
verlte () {
    [  "$1" = "`echo -e "$1\n$2" | sort -V | head -n1`" ]
}

if [ -x "$(command -v opam)" ]; then
    OPAMVERSION=$(opam --version)
    if verlte  $MINOPAMVERSION $OPAMVERSION;
    then
	echo "Opam version"  $OPAMVERSION ">=" $MINOPAMVERSION "...good.";
	echo "Removing switch pycoq if present"
	opam switch remove pycoq -y
	echo "Creating switch pycoq with ocaml-variants.4.07.1+flambda"
	opam switch create pycoq ocaml-variants.4.07.1+flambda -y
	opam install coq -y
	opam pin coq-serapi git+https://github.com/pestun/coq-serapi#allowsprop -y
	opam install coq-serapi -y
	opam install menhir -y
    else
	echo "Error: missing opam version >="  $MINOPAMVERSION
	exit -1
    fi
fi
   
    
