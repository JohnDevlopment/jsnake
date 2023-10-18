# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

def add_module_path():
    from pathlib import Path
    import sys

    path = (Path.cwd() / ".." / ".." / "src").resolve()

    sys.path.insert(0, str(path))

def get_module_version():
    from pathlib import Path
    import sys

    path = Path(sys.path[0]) / "jsnake" / "__init__.py"
    source = path.read_text()

    import ast
    code = ast.parse(source, __file__)

    for node in code.body:
        match node:
            case ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())],
                            value=ast.Constant(value=value)):
                if name == "__version__":
                    return value

    raise RuntimeError(f"failed to extract version from {path}")

add_module_path()

project = 'JSnake'
copyright = '2023, JohnDevlopment'
author = 'JohnDevlopment'
release = get_module_version()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc"
]

add_module_names = False

templates_path = ['_templates']
exclude_patterns = []

autodoc_default_options = {
    'special-members': "__init__"
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
