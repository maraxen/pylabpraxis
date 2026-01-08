# Contributing to Praxis

Thank you for your interest in contributing to Praxis! This document will help you get started.

## Getting Started

See the installation instructions [here](docs/installation.md). For contributing, you should install Praxis from source.

If this is your first time contributing to open source, check out [How to Open Source](./docs/how-to-open-source.md) for an easy introduction.

It's highly appreciated by the PyLabRobot developers if you communicate what you want to work on, to minimize any duplicate work. You can do this on the [forum](https://forums.PyLabRobot.org/c/Praxis-development/23).

## Development Tips

It is recommend that you use VSCode, as we provide a workspace config in `/.vscode/settings.json`, but you can use any editor you like, of course.

Some VSCode Extensions I'd recommend:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Pylint](https://github.com/microsoft/vscode-pylint)
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
- [mypy](https://marketplace.visualstudio.com/items?itemName=matangover.mypy)

## Agentic Development Workflow

This project uses the `.agents/` directory for AI-assisted development:

- **DEVELOPMENT_MATRIX.md**: Central priority/status tracking
- **backlog/**: Detailed work item specifications
- **prompts/**: Agent dispatch prompts organized by date
- **codestyles/**: Language-specific conventions

See `.agents/README.md` for full documentation.

## Running Tests

Praxis uses `pytest` to run unit tests. Please make sure tests pass when you submit a PR. You can run tests as follows.

```bash
make test # run test on the latest version
```

`pylint` is used to enforce code style. The rc file is `/.pylintrc`. As mentioned above, it is very helpful to have an editor do style checking as you're writing code.

```bash
make lint
```

`mypy` is used to enforce type checking.

```bash
make typecheck
```

## Writing documentation

It is important that you write documentation for your code. As a rule of thumb, all functions and classes, whether public or private, are required to have a docstring. Praxis uses [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). In addition, Praxis uses [type hints](https://docs.python.org/3/library/typing.html) to document the types of variables.

To build the documentation, run `make docs` in the root directory. The documentation will be built in `docs/_build/html`. Run `open docs/_build/html/index.html` to open the documentation in your browser.

## Common Tasks

### Fixing a bug

Bug fixes are an easy way to get started contributing.

Make sure you write a test that fails before your fix and passes after your fix. This ensures that this bug will never occur again. Tests are written in `<filename>_tests.py` files. See [Python's unittest module](https://docs.python.org/3/library/unittest.html) and existing tests for more information. In most cases, adding a few additional lines to an existing test should be sufficient.

## Support

If you have any questions, feel free to reach out using the [Praxis forum](https://forums.PyLabRobot.org).
