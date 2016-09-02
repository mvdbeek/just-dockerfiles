# Location of virtualenv used for development.
VENV?=.venv
# Source virtualenv to execute command (flake8, sphinx, twine, etc...)
IN_VENV=if [ -f $(VENV)/bin/activate ]; then . $(VENV)/bin/activate; fi;

REPORT?=report.xml

help:
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup-venv: ## setup a development virutalenv in current directory
	if [ ! -d $(VENV) ]; then virtualenv $(VENV); exit; fi;
	$(IN_VENV) pip install -r requirements.txt

dump-description: setup-venv # Dump JSON description of recipe
	$(IN_VENV) python dump_description.py $(RECIPE_NAME)

run-test: setup-venv # Run a test.
	$(IN_VENV) py.test run_test.py -k $(RECIPE_NAME) --junit-xml $(REPORT)
