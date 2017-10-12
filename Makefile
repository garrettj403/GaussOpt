# Makefile for GaussOpt
#
# Makefile examples that I drew from:
# https://github.com/pjz/mhi/blob/master/Makefile
# http://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html
#

TEST_PATH=./
GO_PATH=./


all: init update test clean_all


# Install pacakge ------------------------------------------------------------

init:
	python setup.py install


# Install requirements (with Pip) --------------------------------------------

install:
	pip install -r requirements.txt

upgrade:
	pip install -r requirements.txt --upgrade

update: upgrade


# Install requirements (with Conda) ------------------------------------------

install_with_conda:
	conda install --yes --file=requirements.txt

upgrade_with_conda:
	conda upgrade --yes --file=requirements.txt

update_with_conda: upgrade_with_conda


# Run tests (with Py.Test) ---------------------------------------------------

test: clean
	pytest --verbose --color=yes --cov=$(GO_PATH) --cov-report=html $(TEST_PATH) 
	open htmlcov/index.html

install_pytest:
	pip install pytest 
	pip install pytest-cov

clean_test:
	find . -name 'htmlcov' -exec rm -rf {} +
	find . -name '.coverage' -exec rm -rf {} +
	find . -name '.cache' -exec rm -rf {} +
	find . -name '.ipynb_checkpoints' -exec rm -rf {} +


# Build ----------------------------------------------------------------------

build:
	python setup.py sdist

upload:
	twine upload dist/*

register:
	python setup.py register

clean_build:
	rm -rf build/
	rm -rf dist/
	rm MANIFEST


# Clean bytecode -------------------------------------------------------------

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean_all: clean clean_test clean_build


# Misc -----------------------------------------------------------------------

.PHONY: install_with_conda upgrade_with_conda install upgrade update test clean all
