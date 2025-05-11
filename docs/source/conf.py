# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../utils"))
sys.path.insert(0, os.path.abspath("../../onboarding"))
sys.path.insert(0, os.path.abspath("../../onboarding/testing"))

# setup django
os.environ['DJANGO_SETTINGS_MODULE'] = 'fitfocus.settings'
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FitFocus'
copyright = '2025, SETAP-Team2B(2)'
author = 'SETAP-Team2B(2)'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']
exclude_patterns = []

# may have to use all django settings when importing
autodoc_mock_import = ['django']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# including this fixes a warning when building docs
linkcheck_allowed_redirects = {}

autodoc_member_order = "bysource"
# can be "alphabetical" or "groupwise", configures how data is displayed in HTML