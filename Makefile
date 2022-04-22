# Reference: https://stackabuse.com/how-to-write-a-makefile-automating-python-setup-compilation-and-testing/

SHELL:=/bin/bash
PYTHON = python3
APP_NAME = hello_world

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project venv type make setup"
	@echo "To install requirements type make install"
	@echo "To build the project type make build"
	@echo "To test the project type make test"
	@echo "To run the project type make run"
	@echo "------------------------------------"

setup:
	# Create python virtualenv & source it
	${PYTHON} -m venv ~/.${APP_NAME}
	source ~/.${APP_NAME}/bin/activate

install:
	# You should run this from your virtual environment
	pip install --upgrade pip &&\
		pip install -r requirements.txt &&\
		pip install --upgrade build pytest flake8

build:
	python3 -m build

lint:
	# See local hadolint install instructions: https://github.com/hadolint/hadolint
	# This is a linter for Dockerfiles
	hadolint Dockerfile
	# This linter is for python source code, and you should run it inside a virtualenv
	pylint src/${APP_NAME}

scan:
	# Use bandit to scan the app for security issues
	${PYTHON} -m bandit ${APP_NAME}/*

test:
	${PYTHON} -m pytest

run:
	${PYTHON} ${APP_NAME}

clean:
	rm -rf \
		build \
		dist \
		.pytest* \
		*.egg-info \
		tests/__pycache__/ \
		tests/${APP_NAME}/__pycache__/

all: install lint test

.PHONY: build test