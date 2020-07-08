#!/bin/bash
export MAKEFLAGS=-j$(nproc)
make setup-tools-ubuntu
make setup-conda
make setup-python-3.8
make setup-pycoq-venv
source venv/bin/activate
make opam-init
make setup-coq
opam switch pycoq
eval $(opam env)
make test-setup
make test-trace-CompCert
make test-serapi-compcert
make test-trace-MathComp
make test-serapi-mathcomp
make test-trace-bignums
make test-serapi-bignums
