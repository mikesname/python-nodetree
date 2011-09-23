"""
Nodetree decorators.
"""

from __future__ import absolute_import

import inspect
import textwrap

from . import node


def underscore_to_camelcase(value):
    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize
    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def upper_camelcase(value):
    value = underscore_to_camelcase(value)
    return value[0].capitalize() + value[1:]


class makenode(object):
    """Decorate for constructing a node out
    of a single function."""
    def __init__(self, *args, **kwargs):
        assert len(args) > 0, "Nodes must have an output type"
        self.intypes = args[:-1]
        self.outtype = args[-1]
        self.kwargs = kwargs

    def __call__(self, fun):
        argspec = inspect.getargspec(fun)

        def _eval(self):
            args = [self.eval_input(i) for i in range(len(argspec.args))]
            return fun(*args)

        doc = fun.__doc__ if not fun.__doc__ is None \
                else "No description provided"
        clsname = upper_camelcase(fun.__name__)
        ns = upper_camelcase(fun.__module__.split(".")[-1])
        clsdict = dict(
            __module__ = fun.__module__,
            __doc__ = doc,
            _eval = _eval,
            arity = len(self.intypes),
            intypes = self.intypes,
            outtype = self.outtype,
            description = textwrap.dedent(fun.__doc__),
            name = "%s::%s" % (ns, clsname),
        )
        clsdict.update(self.kwargs)
        return type(clsname + "Node", (node.Node,), clsdict)()


class Node(object):
    """Decorator to turn nodes into classes."""
    def __init__(self, *args, **kwargs):
        assert len(args) > 0, "Nodes must have an output type"
        self.intypes = args[:-1]
        self.outtype = args[-1]
        self.kwargs = kwargs

    def __call__(self, cls):
        argspec = inspect.getargspec(cls.run)

        def _eval(self):
            args = [self.eval_input(i) for i in range(1, len(argspec.args))]
            return self.run(*args)

        doc = cls.__doc__ if not cls.__doc__ is None \
                else ""
        clsname = upper_camelcase(cls.__name__)
        ns = upper_camelcase(cls.__module__.split(".")[-1])
        clsdict = dict(**cls.__dict__)
        clsdict.update(
            __module__ = cls.__module__,
            __doc__ = doc,
            _eval = _eval,
            arity = len(self.intypes),
            intypes = self.intypes,
            outtype = self.outtype,
            description = textwrap.dedent(doc).strip(),
            name = "%s::%s" % (ns, clsname),
        )
        clsdict.update(self.kwargs)
        return type(clsname, cls.__bases__, clsdict)

