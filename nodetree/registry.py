"""
Registry class and global node and type registys.

This class was adapted from the Celery Project's task registry.
"""

import inspect

class NotRegistered(KeyError):
    pass


class Registry(dict):
    NotRegistered = NotRegistered

    def register(self, thing):
        """Register a thing class in the thing registry."""
        self[thing.name] = inspect.isclass(thing) and thing or thing.__class__

    def unregister(self, name):
        """Unregister thing by name."""
        try:
            # Might be a thing class
            name = name.name
        except AttributeError:
            pass
        self.pop(name)

    def get_by_attr(self, attr, *values):
        """Return all things of a specific type that have a matching attr.
        If `value` is given, only return things where the attr value matches."""
        ret = {}
        for name, thing in self.iteritems():
            if hasattr(thing, attr) and len(values) == 0\
                    or hasattr(thing, name) and getattr(thing, name) in values:
                ret[name] = thing
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


nodes = Registry()
types = Registry()


