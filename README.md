
The pip distribution package pycoq provides two python packages:

- serlib

- pycoq


## pycoq

pycoq is a python library that provides API to coq-serapi 

## serlib 

serlib is a python library that exposes C++ s-expression parser

See https://bagnalla.github.io/sexp-trees/ for s-expression visualisation. 


## Install on Linux

### Install python=3.8. 
If conda https://docs.conda.io/en/latest/miniconda.html#miniconda is installed, run
```
conda create -n pycoq python=3.8
conda activate pycoq
```

### Install opam=2.0.5
On Ubuntu 20.04 run 
```
apt-get install opam
```
See https://opam.ocaml.org/doc/Install.html for other systems


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
cd tests
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












