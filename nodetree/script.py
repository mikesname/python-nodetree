"""Object representation of a Node script."""

from __future__ import absolute_import

from . import node, registry, exceptions


class Script(object):
    """Object describing a node workflow."""
    def __init__(self, script, nodekwargs=None):
        """Initialiser."""
        self._nodekwargs = nodekwargs if nodekwargs is not None \
                else {}
        self._error = None
        self._tree = {}
        self._meta = []
        self._nodemeta = {}
        self._build_tree(script)

    def _build_tree(self, script):
        """Wire up the nodes in tree order."""
        for name, n in script.iteritems():
            if name.startswith("__"):
                self._meta.append((name, n))
                continue
            for attr, val in n.iteritems():
                if attr.startswith("__"):
                    self._nodemeta[name] = (attr, val)
            self._tree[name] = self.new_node(n["type"], name, n["params"])
            self._tree[name].ignored = n.get("ignored", False)
        for name, n in script.iteritems():
            if name.startswith("__"):
                continue
            for i in range(len(n["inputs"])):
                self._tree[name].set_input(i, self._tree.get(n["inputs"][i]))

    def add_node(self, type, label, params):
        """Add a node of the given type, with the given label."""
        self._tree[label] = self.new_node(type, label, params)        
        return self._tree[label]

    def replace_node(self, old, new):
        """Replace a node in the tree with a new one."""
        assert self._tree[old.label], "Node being replaced '%s' is not in tree" % old.label
        if not old.arity == new.arity:
            raise exceptions.ScriptError("Replacement node must have the same "
                    "number of inputs as that being replaced.")
        for i in range(old.arity):
            new.set_input(i, old.input(i))
        for node in self._tree.values():
            for i in range(node.arity):
                if node.input(i) == old:
                    node.set_input(i, new)
        del self._tree[old.label]
        self._tree[new.label] = new                    

    def get_node(self, name):
        """Find a node in the tree."""
        return self._tree.get(name)

    def new_node(self, type, label, params):
        cls = registry.nodes[type]
        n = cls(label=label, **self._nodekwargs)
        for p, v in params:
            n.set_param(p, v)
        return n

    def get_nodes_by_attr(self, name, value):
        """Find a node by attibute value."""
        nodes = []
        for node in self._tree.itervalues():
            if hasattr(node, name) and getattr(node, name) == value:
                nodes.append(node)
        return nodes

    def get_detached_inputs(self):
        """Get nodes that have an unplugged input."""
        return [n for n in self._tree.itervalues() \
                if n.inputs() and None in n.inputs()] 

    def get_terminals(self):
        """Get nodes that end a branch."""
        return [n for n in self._tree.itervalues() \
                if not n.has_parents()]

    def validate(self):
        """Call 'validate' on all nodes."""
        errors = {}
        for name, n in self._tree.iteritems():
            try:
                n.validate()
            except exceptions.ValidationError, err:
                errors[name] = err.message
        return errors                

    def serialize(self):
        """Serialize the script to a plain dictionary."""
        out = {}
        for name, node in self._tree.iteritems():
            out[name] = dict(
                type=node.name,
                inputs=[n.label if n else n for n in node.inputs()],
                params=[(p["name"], node._params[p["name"]]) for p \
                    in node.parameters if node._params.get(p["name"])],
            )
            meta = self._nodemeta.get(name)
            if meta is not None:
                out[name][meta[0]] = meta[1]
        return out            


