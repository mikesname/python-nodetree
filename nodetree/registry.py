"""
Registry class and global node registry.

This class was adapted from the Celery Project's task registry.
"""

import inspect

class NotRegistered(KeyError):
    pass


class NodeRegistry(dict):
    NotRegistered = NotRegistered

    def register(self, node):
        """Register a node class in the node registry."""
        self[node.name] = inspect.isclass(node) and node or node.__class__

    def unregister(self, name):
        """Unregister node by name."""
        try:
            # Might be a node class
            name = name.name
        except AttributeError:
            pass
        self.pop(name)

    def get_by_attr(self, attr, *values):
        """Return all nodes of a specific type that have a matching attr.
        If `value` is given, only return nodes where the attr value matches."""
        ret = {}
        for name, node in self.iteritems():
            if hasattr(node, attr) and len(values) == 0\
                    or hasattr(node, name) and getattr(node, name) in values:
                ret[name] = node
        return ret                

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            raise self.NotRegistered(key)

    def pop(self, key, *args):
        try:
            return dict.pop(self, key, *args)
        except KeyError:
            raise self.NotRegistered(key)


nodes = NodeRegistry()


