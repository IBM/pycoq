# requires python3.8
# to install python3.8 in conda: 
# conda create -n your_env_name python=3.8
# conda activate your_env_name

# requires opam=2.0.5
# to install opam=2.0.5 in ubuntu 20.04
# apt-get install opam

PYTHON3=python3.8

setup-pycoq-dev:
	@echo "removing local python venv..."
	rm -fr venv
	@echo "creating local python venv..."
	$(PYTHON3) -m venv venv
	@echo "activating local python venv with source venv/bin/activate..."
	@echo "installing pycoq dev dependencies..."
	@echo "installing pycoq in venv in editable mode with pip install -e ."
	. venv/bin/activate ; pip install -r requirements-dev.txt ; pip install -e .
	@echo "to activate pycoq venv: . venv/bin/activate"
