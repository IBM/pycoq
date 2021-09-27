
The pip distribution package pycoq provides two python packages:

- serlib

- pycoq


## pycoq

`pycoq` is a python library that provides interface to Coq using the serialization coq-serapi  https://github.com/ejgallego/coq-serapi

## serlib

`serlib` is a python library providing s-expression parser implemented in C++

## Install on Linux

Currently we support only the Linux platform. 

### External dependencies 

#### opam 
The pycoq calls `opam` package manager to install and run the coq-serapi and coq binaries.
The pycoq assumes that `opam` binary of version 2.* is in the `$PATH`.

On Ubuntu 20.04 install opam with `sudo apt-get install opam`.
See https://opam.ocaml.org/doc/Install.html for other systems. 

#### strace
The pycoq calls `strace` to inspect the building of coq-projects to prepare the context. The pycoq assumes  
that `strace` is in the `$PATH`. 

On Ubuntu 20.04 install strace with `sudo apt-get install strace`.
See https://github.com/strace/strace for other systems.


### Install from github
Assuming `python>=3.8` and `pip` are in your python environment (we recommend to use conda or python venv) to install from github run
```
pip install git+https://github.com/IBM/pycoq
```

### Test your setup
From your python environment with `pycoq` installed run
```
pytest --pyargs pycoq
```

### Config pycoq
The location of the project directory, debug level and other parameters can be specified in the config file `$HOME/.pycoq`

### Uninstall pycoq 
From your python environment with `pycoq` installed run
```
pip uninstall pycoq
```
By default, pycoq uses directory `$HOME/.local/share/pycoq` to store temporary files such as the opam repository, project files and the logs.
To remove the project directory:
```
rm -fr $HOME/.local/share/pycoq
```
To remove the config file:
```
rm $HOME/.pycoq
```

## Using pycoq
For basics see the example `tutorial/tutorial_pycoq.py` and the test scripts in `pycoq/tests`.

## Build pycoq in Docker
Install docker, git clone the source repository and from the directory containing Dockerfile run
```
docker build -t pycoq:test .
```
to verify the setup and test of pycoq in docker container on linux
