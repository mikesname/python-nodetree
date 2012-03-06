"""
Nodetree macro class.  Aggregations of nodes.

A macro is simply a normal JSON node tree, but one that has to
obey a few simple rules.  Most importantly, it can only have
one terminal node, i.e. the output of the macro.  Any nodes with
unconnected inputs are treated as the inputs of the macro.

Macro trees (the JSON) also have stricter metadata requirements
than standard trees.  They MUST provide a `name` attribute (which
is used as the macro's name.  Optional, but typically used, is a
list of _exposed parameters_ which is how the contained nodes
are exposed.  A validation error will occur if nodes have parameters
that are not exposed but do not have default values.
"""

import json

from . import node, exceptions, script


class MacroError(exceptions.NodeError):
    """Something went wrong loading a macro."""


class MacroNode(node.Node):
    """Base class of macro nodes.  Knows how to run
    its tree payload."""

    def process(self):
        pass


def load_macro(jsonfile):
    """Create a new node type from the given JSON file.  Typically
    this function is called at startup."""

    jsontree = None
    try:
        with open(jsonfile, "r") as fh:
            jsontree = json.load(fh)
    except ValueError:
        raise MacroError("Invalid JSON in macro: %s" % jsonfile)

    meta = jsontree.get("__meta"):
    if meta is None:
        raise MacroError("No metadata found in macro file: %s" % jsonfile)
    name = meta.get("name")
    if name is None:
        raise MacroError("No 'name' metadata found in macro file: %s" % jsonfile)
    # TODO: continue



