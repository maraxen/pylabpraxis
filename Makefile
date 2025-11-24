ifeq ($(shell test -e ./env/ && echo yes),yes)
	BIN=env/bin/
	$(info Using virtualenv in env)
endif

.PHONY: docs lint format test

docs:
	sphinx-build -b html docs docs/build/ -j 1 -W

clean-docs:
	rm -rf docs/build
	rm -rf docs/_autosummary

# The lint target now uses 'ruff check'
lint:
	$(BIN)ruff check .

# It's common to add a 'format' target when using ruff
format:
	$(BIN)ruff format .

test:
	$(BIN)python -m pytest -s -v

clear-pyc:
	find . -name "*.pyc" | xargs rm
	find . -name "*__pycache__" | xargs rm -r
