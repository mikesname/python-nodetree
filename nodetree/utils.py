"""
Utils for dealing with Nodes/Plugins.
"""

import json
import node
import types



class NodeEncoder(json.JSONEncoder):
    """
    Encoder for JSONifying nodes.
    """
    def default(self, n):
        """
        Flatten node for JSON encoding.
        """
        if issubclass(n, node.Node):
            return dict(
                name=n.name,
                description=n.description,
                arity=n.arity,
                stage=n.stage,
                passthrough=n.passthrough,
                parameters=n.parameters,
                intypes=[t.__name__ for t in n.intypes],
                outtype=n.outtype.__name__
            )
        return super(NodeEncoder, self).default(n)            


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

    def __repr__(self):
        return "<Classproperty object>"
