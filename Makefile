SHELL := /bin/bash
jobs:=$(shell nproc)
PYCOQ:=python pycoq/pycoq_old.py $(FLAGS)

COQC=$(shell opam exec --switch pycoq which coqc)


.DEFAULT_GOAL := help

CONDA_PREFIX=miniconda3
CONDA=$(HOME)/$(CONDA_PREFIX)/bin/conda
PYCOQ_CONDA_ENV=pycoq
PYTHON38=$(HOME)/$(CONDA_PREFIX)/envs/$(PYCOQ_CONDA_ENV)/bin/python3

help:
	@echo 'to install system-wide command tools and opam: make setup-tools-ubuntu'
	@echo "to install miniconda to $(HOME)/$(CONDA_PREFIX): make setup-conda"
	@echo 'to create python 3.8 conda env: make setup-python-3.8'
	@echo 'to install coq in opam environment pycoq: make setup-coq'
	@echo 'to activate opam environment pycoq: opam switch pycoq; eval $$(opam env)'
	@echo 'to install pycoq in venv in editable mode: make setup-pycoq-venv'
	@echo 'to activate pycoq venv: source venv/bin/activate'
	@echo 'to desactivate pycoq venv: deactivate'
	@echo 'to initialise test repositories of CompCert and MathComp: make test-setup'
	@echo 'to clean tests: make test-clean'
	@echo 'to test pycoq-trace: make test-trace-CompCert; make test-trace-MathComp'
	@echo 'to test pycoq-serapi: make test-serapi'


setup-tools-ubuntu:
	sudo scripts/setup-tools-ubuntu.sh 

opam-init:
	opam init --bare -n

setup-conda:
	scripts/setup-conda-linux.sh $(CONDA_PREFIX)

setup-python-3.8:
	$(CONDA) create -n $(PYCOQ_CONDA_ENV) -y python=3.8

setup-coq: 
	scripts/setup-coq.sh
	@echo 'to activate opam pycoq environment:'
	@echo 'opam switch pycoq'
	@echo 'eval $$(opam env)'

update-coq-serapi:
	opam pin coq-serapi git+https://github.com/pestun/coq-serapi#v8.11.dev --switch pycoq
	opam reinstall coq-serapi --switch pycoq

setup-pycoq-venv:
	@echo 'installing pycoq in venv in editable mode'
	rm -fr venv
	$(PYTHON38) -m venv venv
	source venv/bin/activate ; pip install -r requirements-dev.txt ;  pip install -e .
	@echo 'to activate python pycoq venv environment source venv/bin/activate'



test-setup: tests/data/math-comp/mathcomp/Makefile tests/data/CompCert/Makefile tests/data/bignums/Makefile

test-clean:
	rm -fr tests/data/math-comp
	rm -fr tests/data/CompCert

tests/data/CompCert/Makefile:
	tests/download_CompCert.sh

tests/data/math-comp/mathcomp/Makefile:
	tests/download_MathComp.sh

tests/data/bignums/Makefile:
	tests/download_BigNums.sh


test-trace-CompCert: tests/data/CompCert/Makefile
	pycoq-trace --executable $(COQC) --workdir tests/data/CompCert opam exec --switch pycoq "make -j$(jobs)" clean
	pycoq-trace --executable $(COQC) --workdir tests/data/CompCert opam exec --switch pycoq "make -j$(jobs)" 

test-trace-MathComp: tests/data/math-comp/mathcomp/Makefile
	pycoq-trace --executable $(COQC) --workdir tests/data/math-comp/mathcomp opam exec --switch pycoq "make -j$(jobs) clean"
	pycoq-trace --executable $(COQC) --workdir tests/data/math-comp/mathcomp opam exec --switch pycoq "make -j$(jobs)"

test-trace-bignums: tests/data/bignums/Makefile
	pycoq-trace --executable $(COQC) --workdir tests/data/bignums opam exec --switch pycoq "make -j$(jobs) clean"
	pycoq-trace --executable $(COQC) --workdir tests/data/bignums opam exec --switch pycoq "make -j$(jobs)"

test-serapi-compcert: tests/data/CompCert/lib/UnionFind.v._pycoq_context
	python tests/test-serapi.py --save-serapi-log --log tests/log-serapi-compcert.txt --workers 40  --with-context  tests/data/CompCert 

test-serapi-mathcomp:
	python tests/test-serapi.py --save-serapi-log --log tests/log-serapi-mathcomp.txt  --workers 40 --with-context tests/data/math-comp/mathcomp

test-serapi-bignums:
	python tests/test-serapi.py --save-serapi-log --log tests/log-serapi-bignums.txt  --workers $(jobs)  --with-context tests/data/bignums

test-serapi-small: tests/data/small/b.v
	python tests/test-serapi.py --workdir tests/data/small --log tests/log-serapi-small.log --save-serapi-log tests/data/small 




art1: data/project1/article1.v
	$(PYCOQ)  --debug 1 --pool 1 -f data/project1/article1.v

art2: data/project1/article2.v
	$(PYCOQ)  --debug 1 --pool 1 -f data/project1/article2.v

art3: data/project1/article3.v
	$(PYCOQ) --debug 3 --pool 1 -f data/project1/article3.v 

art4: data/project1/article4.v
	$(PYCOQ) --debug 3 --pool 1  -f data/project1/article4.v 


project3: data/project3
	$(PYCOQ)  --debug 3 --pool 1 --file data/project3


compcert: $(DATA)/CompCert
	$(PYCOQ)  --only-with-coqlog --debug 3 --pool $(jobs) -f $(DATA)/CompCert --results res_compcert_8.11

compcert.backend: $(DATA)/CompCert
	$(PYCOQ) --only-with-coqlog --debug 3 --pool $(jobs) -f $(DATA)/CompCert/backend --results res_compcert_backend8.11

compcert.common: $(DATA)/CompCert
	$(PYCOQ) --only-with-coqlog --debug 3 --pool $(jobs) -f $(DATA)/CompCert/common --results res_compcert_common8.11

compcert.check: $(DATA)/CompCert
	find $(DATA)/CompCert -name "*.pycoqlog"
	find $(DATA)/CompCert -name "*.pycoqlog" -exec grep -l ERROR {} \;

compcert.common.check: $(DATA)/CompCert
	find $(DATA)/CompCert/common -name "*.pycoqlog"
	find $(DATA)/CompCert/common -name "*.pycoqlog" -exec grep -l ERROR {} \;
