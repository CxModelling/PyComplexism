"""Sphinx configuration."""
project = "PyCx"
author = "TimeWz667"
copyright = "2023, TimeWz667"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
