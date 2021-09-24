
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



## Test pycoq
Check pycoq setup by running the tests in the source dir and see examples of the API
```
cd pycoq/tests
pytest
```

## Uninstall pycoq 
In the default configuration pycoq uses directory `$HOME/.local/share/pycoq` to store opam repository and the pycoq.log. 
To remove it run
```
rm -fr $HOME/.local/share/pycoq
```

## Build pycoq in Docker
Install docker and from the directory containing Dockerfile run
```
docker build -t pycoq:test .
```
to verify the setup and test of pycoq in docker container on linux
