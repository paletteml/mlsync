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
# import myst_parser, sphinx_rtd_theme
sys.path.insert(0, os.path.abspath('../../'))
from pathlib import Path

# The readme that already exists
readme_path = Path(__file__).parent.resolve().parent / "../README.md"
# We copy a modified version here
readme_target = Path(__file__).parent / "readme.md"

with readme_target.open("w") as outf:
    # Change the title to "Readme"
    outf.write(
        "\n".join(
            [
                "Overview",
                "======",
            ]
        )
    )
    lines = []
    for line in readme_path.read_text().split("\n"):
        if line.startswith("# "):
            # Skip title, because we now use "Readme"
            # Could also simply exclude first line for the same effect
            continue
        lines.append(line)
    outf.write("\n".join(lines))

# -- Project information -----------------------------------------------------

project = 'mlsync'
copyright = '2022, Andre and Kartik'
author = 'Andre and Kartik'

# The full version, including alpha/beta/rc tags
release = '0.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', # for docstring support
                # 'recommonmark', # For markdown
                'myst_parser', # For myst
                ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
source_suffix = [".rst", ".md"] # for markdown

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

##### Custom settings #####

## Adding Markdown support
