"""Sphinx configuration file for Praxis documentation."""
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "Praxis"
copyright = "2025, Marielle Russo"
author = "Marielle Russo"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
extensions = [
  "sphinx.ext.autodoc",
  "sphinx.ext.viewcode",
  "sphinx.ext.napoleon",
  "sphinx.ext.intersphinx",
  "sphinx.ext.autosummary",
  "myst_nb",
  "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

html_theme_options = {
  "repository_url": "https://github.com/maraxen/praxis",
  "use_repository_button": True,
  "use_issues_button": True,
  "use_edit_page_button": True,
  "path_to_docs": "docs",
}

# -- Extension configuration -------------------------------------------------
# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# Autodoc settings
autodoc_default_options = {
  "members": True,
  "undoc-members": True,
  "show-inheritance": True,
}

# Autosummary settings
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
  "python": ("https://docs.python.org/3", None),
  "fastapi": ("https://fastapi.tiangolo.com", None),
}
