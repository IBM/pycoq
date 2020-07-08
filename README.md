# pycoq: python library to interface with coq theorem prover

## Quick Install on Ubuntu 18.04.3 

Clone the repo and execute `pycoq_install.sh` from it
```
cd pycoq
./install-pycoq.sh
```
The script installs linux developer tools, opam package manager + coq, miniconda with conda env pycoq and python 3.8, and pycoq package in python 3.8 venv environment. Consult the instructions below for individual stages. 

## Stages of install on Linux / Ubuntu 18.04.3 

To speed up build on multicore systems set the make flag in the environment 

`export MAKEFLAGS=-j$(nproc)`

- Clone the `pycoq` repository

`git clone <reponame>`
    
`cd pycoq`

- Install common build tools and opam package manager on ubuntu if missing

`make setup-tools-ubuntu`
    
- Install miniconda to `CONDA_PREFIX` specified in `Makefile` if missing

`make setup-conda`

(consult documentation for `conda init` for permanent hook shell activation)

- Create conda environment pycoq with python 3.8 if missing

`make setup-python-3.8`

- To setup pycoq in venv in editable mode: 

`make setup-pycoq-venv`

- To activate / deactivate python pycoq venv:

`source venv/bin/activate` / `deactivate`

If pycoq is succesfully installed and activated, the pycoq tool
`pycoq-trace` should be available in the path and executable 

- Install coq into opam environment pycoq if missing

`make setup-coq`

- To activate opam environment pycoq 

`opam switch pycoq`

`eval $(opam env)`

(consult documentation of `opam init` for hook shell activation or shell config)

- To download and initialise test repos of coq libraries  CompCert and MathComp

`make test-setup`

- To compile tests with factory coq and record the context of coqc calls

`make test-trace-CompCert`

`make test-trace-MathComp`

`make test-serapi`

