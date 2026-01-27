# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'AttackMate'
copyright = '2023, Wolfgang Hotwagner'
author = 'Wolfgang Hotwagner'
release = '0.6.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_multiversion',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinx_toolbox.confval']

# Configure what branches/tags to include
smv_tag_whitelist = r'^v?\d+\.\d+\.\d+$'  # Includes tags like v1.0.0
smv_branch_whitelist = r'^(main|feature_github_pages)$'        # Includes the main branch
smv_remote_whitelist = None      # Only look at origin

templates_path = ['_templates']
exclude_patterns = []  # type: ignore

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'logo_only': False,
    'navigation_depth': 2,
    'collapse_navigation': True,
}

html_sidebars = {
    '**': [
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'versions.html',
    ],
}

html_context = {
    'display_lower_left': True,
}
