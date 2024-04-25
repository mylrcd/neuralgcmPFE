# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# Print Python environment info for easier debugging on ReadTheDocs

import sys
import subprocess
import dinosaur  # verify this works
import neuralgcm  # verify this works

print("python exec:", sys.executable)
print("sys.path:", sys.path)
print("pip environment:")
subprocess.run([sys.executable, "-m", "pip", "list"])

print(f"dinosaur: {dinosaur.__version__}, {dinosaur.__file__}")
print(f"neuralgcm: {neuralgcm.__version__}, {neuralgcm.__file__}")

# -- Project information -----------------------------------------------------

project = 'NeuralGCM'
copyright = '2024, Google LCC'
author = 'NeuralGCM authors'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'myst_nb',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', '_templates', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    # "xarray": ("https://xarray.pydata.org/en/latest/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Extension config

autosummary_generate = True

# https://myst-nb.readthedocs.io/en/latest/use/execute.html
jupyter_execute_notebooks = "cache"
# https://myst-nb.readthedocs.io/en/latest/use/formatting_outputs.html#removing-stdout-and-stderr
nb_output_stderr = "remove-warn"

# https://stackoverflow.com/a/66295922/809705
autodoc_typehints = "description"