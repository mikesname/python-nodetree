"""
Base class for OCR nodes.
"""

from __future__ import absolute_import

import sys
import textwrap
import logging
FORMAT = '%(levelname)-5s %(module)s: %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger("Node")
LOGGER.setLevel(logging.INFO)

from . import cache, registry


class NodeError(Exception):
    def __init__(self, node, msg):
        super(NodeError, self).__init__("%s: %s (arity: %d)" % (node.label, msg, node.arity))
        self.node = node
        self.message = msg

class UnsetParameterError(NodeError):
    pass

class ValidationError(NodeError):
    pass

class InvalidParameterError(NodeError):
    pass

class InputOutOfRange(NodeError):
    pass

class CircularDagError(NodeError):
    pass

def noop_abort_func(*args):
    """
    A function for nodes to call that signals that 
    they should abort.  By default it does nothing.
    """
    return False

def noop_progress_func(*args):
    """
    A function for nodes to call that reports on their
    progress.  By default it does nothing.
    """
    pass


class NodeType(type):
    """Meta class for nodes.  Automatically registers
    the node with the node registry, and if necessary
    generates name, arity, description, and passthrough
    class-level attributes."""

    def __new__(cls, name, bases, attrs):
        new = super(NodeType, cls).__new__
        node_module = attrs.get("__module__") or "__main__"

         # Abstract class: abstract attribute should not be inherited.
        if attrs.pop("abstract", None) or not attrs.get("autoregister", True):
            return new(cls, name, bases, attrs)

        # Automatically generate missing/empty name, description, arity.
        autoname = False
        if not attrs.get("name"):
            try:
                module_name = sys.modules[node_module].__name__
            except KeyError:  # pragma: no cover
                # Fix for manage.py shell_plus (Issue #366).
                module_name = node_module
            attrs["name"] = '.'.join([module_name.split(".")[-1], name])
            autoname = True

        node_name = attrs["name"]
        if node_name not in registry.nodes:
            nodecls = new(cls, name, bases, attrs)
            nodecls.arity = attrs.get("arity", len(nodecls.intypes))

            if attrs.get("description") is None:
                doc = attrs.get("__doc__") or ""
                nodecls.description = textwrap.dedent(doc).strip()
            if attrs.get("passthrough") is None:
                nodecls.passthrough = 0
            registry.nodes.register(nodecls)
        return registry.nodes[node_name]

    def __repr__(cls):
        return "<class Node %s>" % cls.name
            


class Node(object):
    """
    Node object.  Evaluates some input and
    return the output.    
    """

    __metaclass__ = NodeType
    abstract = True
    intypes = [object]
    outtype = object
    parameters = []

    def __init__(self, label=None, abort_func=None, 
                cacher=None,
                progress_func=None, logger=None, ignored=False):
        """
        Initialise a node.
        """
        self.abort_func = abort_func if abort_func is not None \
                else noop_abort_func
        self.logger = logger if logger is not None \
                else LOGGER
        self.progress_func = progress_func if progress_func is not None \
                else noop_progress_func
        self._cacher = cacher if cacher is not None \
                else cache.BasicCacher(logger=self.logger)
        self._params = {}
        self.label = label
        self._parents = []
        self._inputs = [None for n in range(self.arity)]
        self._inputdata = [None for n in range(self.arity)]
        self.logger.debug("Initialised %s with cacher: %s" % (self.label, self._cacher))
        self.ignored = ignored

    def set_param(self, param, name):
        """
        Set a parameter.
        """
        self._params[param] = name
        self.mark_dirty()

    def _set_p(self, p, v):
        """
        Set a parameter internally.
        """
        pass

    def _eval(self):
        """
        Perform actual processing.
        """
        pass

    def add_parent(self, n):
        """
        Add a parent node.
        """
        if self == n:
            raise CircularDagError(self, "added as parent to self")
        if not n in self._parents:
            self._parents.append(n)

    def has_parents(self):
        """
        Check if the node is a terminal node
        or if there's a tree further down.
        """
        return bool(len(self._parents))

    def input(self, num):
        """
        Get an input.
        """
        if num > len(self._inputs) - 1:
            raise InputOutOfRange(self, "Input '%d'" % num)
        return self._inputs[num]

    def inputs(self):
        """
        Return list of inputs.
        """
        return self._inputs

    def set_input(self, num, n):
        """
        Set an input.

        num: 0-based input number
        node: input node
        """
        if num > len(self._inputs) - 1:
            raise InputOutOfRange(self, "Input '%d'" % num)
        if n is not None:
            n.add_parent(self)
        self._inputs[num] = n

    def mark_dirty(self):
        """
        Tell the node it needs to reevaluate.
        """
        self.logger.debug("%s marked dirty", self)
        for parent in self._parents:
            parent.mark_dirty()
        self._cacher.clear_cache(self)

    def set_cache(self, cache):
        """
        Set the cache on a node, preventing it
        from eval'ing its inputs.
        """
        self._cacher.set_cache(self, cache)

    def eval_input(self, num):
        """
        Eval an input node.
        """
        if self._inputs[num] is not None:
            return self._inputs[num].eval()

    def eval_inputs(self):
        """
        Eval all inputs and store the data in
        self._inputdata.
        """
        for i in range(len(self._inputs)):
            self._inputdata[i] = self.eval_input(i)

    def get_input_data(self, num):
        """
        Fetch data for a given input, eval'ing
        it if necessary.
        """
        if self._inputdata[num] is None:
            self._inputdata[num] = self.eval_input(num)
            return self._inputdata[num]
        return self._inputdata[num]

    def validate(self, skipinputs=False):
        """
        Check params are present and correct.
        """
        if self.arity > 0 and not skipinputs:
            for n in self._inputs:
                if n is not None:
                    n.validate()
        self._validate()                    

    def _validate(self):
        """
        Check the node can execute properly.
        """
        self._validate_inputs()
        self._validate_parameters()

    def _validate_inputs(self):
        """Ensure parameters in/out have compatible types."""
        for i in range(len(self._inputs)):
            if self._inputs[i] is None:
                raise ValidationError(self, "missing input '%d'" % i)
            if not issubclass(self._inputs[i].outtype, self.intypes[i]):
                raise ValidationError(self,
                        "incorrect input type '%s' for input '%d': should be '%s'" % (
                            self._inputs[i].outtype.__name__, i, self.intypes[i].__name__))

    def _validate_parameters(self):
        """Ensure parameters are sane."""
        for p in self.parameters:
            choices = p.get("choices")
            if choices is None:
                continue
            val = self._params.get(p.get("name"))
            if not val in choices:
                raise ValidationError(self, 
                        "parameter '%s'='%s' is not a valid value, must be one of: %s" % (
                            p.get("name"), val, ", ".join(choices)))

    def hash_value(self):
        """
        Get a representation of this
        node's current state.  This is a data
        structure the node type, it's
        parameters, and it's children's hash_values.
        """
        # if ignore, return the hash of the
        # passthrough input
        if self.arity > 0 and self.ignored:
            return self._inputs[self.passthrough].hash_value()

        def makesafe(val):
            if isinstance(val, unicode):
                return val.encode()
            elif isinstance(val, float):
                return str(val)
            return val

        return dict(
            name=self.name.encode(),
            params=[[makesafe(v) for v in p] for p \
                    in self._params.iteritems()],
            children=[n.hash_value() for n in self._inputs \
                    if n is not None]
        )

    def null_data(self):
        """
        What we return when ignored.
        """
        if self.arity > 0:
            return self.eval_input(self.passthrough)

    def first_active(self):
        """
        Get the first node in the tree that is
        active.  If not ignored this is 'self'.
        """
        if self.arity > 0 and self.ignored:
            return self._inputs[self.passthrough].first_active()
        return self

    def eval(self):
        """
        Eval the node.
        """
        if self.ignored:
            self.logger.debug("Ignoring node: %s", self)
            return self.null_data()
        self.validate()
        for p, v in self._params.iteritems():
            self.logger.debug("Set Param %s.%s -> %s",
                    self, p, v)
            self._set_p(p, v)            
        if self._cacher.has_cache(self):
            self.logger.debug("%s returning cached input", self)
            return self._cacher.get_cache(self)
        self.eval_inputs()
        self.logger.debug("Evaluating '%s' Node", self)
        data = self._eval()
        self._cacher.set_cache(self, data)
        return data

    def __repr__(self):
        return "<%s: %s: %s" % (self.__class__.__name__, self.name, self.label)

    def __str__(self):
        return "%s<%s>" % (self.label, self.name)




