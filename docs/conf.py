# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

sys.path.append(os.path.abspath(".."))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Contacts App'
copyright = '2025, Brelyk'
author = 'Brelyk'
release = '06.04.2025'

# -- General configuration ---------------------------------------------------
# <https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration>

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# <https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output>

html_theme = "nature"
html_static_path = ["_static"]

language = 'ua'

