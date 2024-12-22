# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from flask import Flask
import os

app = Flask(__name__, static_folder=os.path.join('C:\\', 'Users', 'HP', 'Desktop', 'UNI', 'Year 3 FALL', 'SWE', 'project final', 'MindMatters'))
project = 'MindMatters'
copyright = '2024, Nour'
author = 'Nour' 
release = '22/12/2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Automatically document from docstrings
    'sphinx.ext.viewcode',  # Include links to source code
    'sphinxcontrib.httpdomain'  # For documenting RESTful APIs
]

templates_path = ['_templates']
exclude_patterns = []

language = 'python'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
