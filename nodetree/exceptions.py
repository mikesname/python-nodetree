"""
Nodetree exception classes.
"""

class NodeError(Exception):
    """General nodetree error."""
    def __init__(self, msg, node=None):
        self.message = msg
        self.node = node
        super(NodeError, self).__init__("%s: %s" % (node, msg))


class ValidationError(NodeError):
    """Validation of a node's parameters failed."""


class UnsetParameterError(ValidationError):
    """A mandatory parameter was not set."""


class InvalidParameterError(ValidationError):
    """A parameter that took a particular type of value, didn't."""


class InputOutOfRangeError(NodeError):
    """Attempt to connect an input the node didn't possess."""


class CircularDagError(NodeError):
    """A node was connected circularly to its own input."""

class ScriptError(NodeError):
    """Miscellaneous script manipulation errors."""
