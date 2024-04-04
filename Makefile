ifeq ($(shell test -e ./env/ && echo yes),yes)
	BIN=env/bin/
$(info Using virtualenv in env)
endif

.PHONY: docs lint test

docs:
	sphinx-build -b html docs docs/build/ -j 1 -W

clean-docs:
	rm -rf docs/build
	rm -rf docs/_autosummary

lint:
	$(BIN)python -m pylint pylabpraxis --disable=C0103

test:
	$(BIN)python -m pytest -s -v

typecheck:
	$(BIN)python -m mypy pylabpraxis --check-untyped-defs

clear-pyc:
	find . -name "*.pyc" | xargs rm
	find . -name "*__pycache__" | xargs rm -r

