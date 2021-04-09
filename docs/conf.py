# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------

project = 'Crafting'
copyright = '2021, Mathïs Fédérico'
author = 'Mathïs Fédérico'

# The full version, including alpha/beta/rc tags
def get_version():
    version_file = open('../VERSION')
    return version_file.read().strip()

version = get_version()
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage'
]

master_doc = 'index'
autoapi_dirs = ['../crafting']
autodoc_mock_imports = ["pygame", "gym", "pygame_menu"]
autodoc_default_options = {
    'member-order': 'bysource',
    'undoc-members': True,
}
add_module_names = False
# pygments_style = 'monokai'

intersphinx_mapping = {
    'python': ('https://docs.python.org/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    'networkx': ('https://networkx.org/documentation/latest', None),
    'matplotlib': ('http://matplotlib.sourceforge.net/', None)
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'canonical_url': '',
    'analytics_id': 'UA-XXXXXXX-1',  #  Provided by Google in your dashboard
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'both',
    'style_external_links': '#ff9900',
    'style_nav_header_background': '#ff9900',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# -- Version control GitHub --------------------------------------------------
html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": "MathisFederico", # Username
    "github_repo": "LearnRL", # Repo name
    "github_version": "dev", # Version
    "conf_py_path": "/docs/", # Path in the checkout to the docs root
}

html_static_path = ['_static']
def setup(app):
    app.add_css_file('styles/custom.css')
