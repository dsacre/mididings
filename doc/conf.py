# -*- coding: utf-8 -*-
#
import sys, os

sys.path.insert(0, os.path.abspath('..'))

extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.fulltoc']

templates_path = ['templates']
html_theme_path = ['theme']
exclude_patterns = ['build']

source_suffix = '.rst'
master_doc = 'index'

project = u'mididings'
copyright = u'2008-2014, Dominic Sacré'
version = ''
release = ''

html_theme = 'nasophon'
html_copy_source = False
pygments_style = 'sphinx'

add_module_names = False
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'undoc-members']


from sphinx.ext.autodoc import py_ext_sig_re
from sphinx.util.docstrings import prepare_docstring
from sphinx.domains.python import PyModulelevel
from sphinx import addnodes
import re


def process_docstring(app, what, name, obj, options, lines):
    """
    Remove leading function signatures from docstring.
    """
    while len(lines) and py_ext_sig_re.match(lines[0]) is not None:
        del lines[0]

def process_signature(app, what, name, obj, options, signature, return_annotation):
    """
    Replace function signature with those specified in the docstring.
    """
    if hasattr(obj, '__doc__') and obj.__doc__ is not None:
        lines = prepare_docstring(obj.__doc__)
        siglines = []

        for line in lines:
            if py_ext_sig_re.match(line) is not None:
                siglines.append(line)
            else:
                break

        if len(siglines):
            siglines[0] = siglines[0][siglines[0].index('('):]
            return ('\n'.join(siglines), None)

    return (signature, return_annotation)


class DingsFunction(PyModulelevel):
    """
    Stripped-down version of the 'function::' directive that accepts an
    additional argument in angle brackets, used to specify the node's
    'fullname' attribute. This allows proper cross-references to mididings
    operators.
    """
    def handle_signature(self, sig, signode):
        m = re.match('(.*) <([\w.]*)>', sig)
        if m:
            op = m.group(1)
            name = m.group(2)
            modname = self.options.get('module', self.env.temp_data.get('py:module'))

            signode['module'] = modname
            signode['class'] = ''
            signode['fullname'] = name
            signode += addnodes.desc_name(op, op)

            return name, None
        else:
            return super(PyModulelevel, self).handle_signature(sig, signode)


def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
    app.connect('autodoc-process-signature', process_signature)
    app.add_directive('dingsfun', DingsFunction)
