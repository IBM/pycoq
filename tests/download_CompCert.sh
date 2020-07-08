#!/bin/bash
rm -fr tests/data/CompCert
git clone https://github.com/AbsInt/CompCert tests/data/CompCert
(opam switch pycoq && eval $(opam env) && cd tests/data/CompCert && ./configure x86_64-linux)

