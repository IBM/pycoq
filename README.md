
The pip distribution package pycoq provides two python packages:

- serlib

- pycoq


## pycoq

pycoq is a python library that provides API to coq-serapi 

## serlib 

serlib is a python library that exposes C++ s-expression parser

See https://bagnalla.github.io/sexp-trees/ for s-expression visualisation. 


## Install on Linux

We provide quick instructions for installing pycoq on Linux. Other platforms are not currently supported. 

### Provide python3
We assume that python3 is available in the shell environment (the current release of pycoq is tested on python 3.8). For example, you can provide python3 using conda as follows (assuming  https://docs.conda.io/en/latest/miniconda.html#miniconda is installed)
```
conda create -n pycoq python=3.8
conda activate pycoq
```

### Provide opam of version 2.*
We assume that opam of version = 2.* is available in the shell environment. On Ubuntu 20.04 you can install opam with
```
apt-get install opam
```
See opam install instructions https://opam.ocaml.org/doc/Install.html for other distros.


### Install pycoq
To install pycoq in development mode (editable version in venv environment) under the source
directory run

```
make setup-pycoq-dev
```

### Activate pycoq venv
```
. venv/bin/activate
```


### Run tests
```
cd pycoq/tests
pytest
```


### Deactivate
To quit from the venv 
```
deactivate
```

### Uninstall 
In the default configuration pycoq uses directory `$HOME/.local/share/pycoq` to store opam repository and other files. To remove it run
```
rm -fr $HOME/.local/share/pycoq
```












