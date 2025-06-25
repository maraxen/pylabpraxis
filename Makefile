ifeq ($(shell test -e ./env/ && echo yes),yes)
  BIN=env/bin/
$(info Using virtualenv in env)
endif

.PHONY: docs lint format test typecheck

docs:
  sphinx-build -b html docs docs/build/ -j 1 -W

clean-docs:
  rm -rf docs/build
  rm -rf docs/_autosummary

# The lint target now uses 'ruff check'
lint:
  $(BIN)ruff check pylabpraxis

# It's common to add a 'format' target when using ruff
format:
  $(BIN)ruff format pylabpraxis

test:
  $(BIN)python -m pytest -s -v

typecheck:
  $(BIN)python -m mypy pylabpraxis --check-untyped-defs

clear-pyc:
  find . -name "*.pyc" | xargs rm
  find . -name "*__pycache__" | xargs rm -r