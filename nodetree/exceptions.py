"""
Nodetree exception classes.
"""

class NodeError(Exception):
    def __init__(self, msg, node=None):
        self.message = msg
        self.node = node
        super(NodeError, self).__init__("%s: %s" % (node, msg))

class UnsetParameterError(NodeError):
    pass

class ValidationError(NodeError):
    pass

class InvalidParameterError(NodeError):
    pass

class InputOutOfRangeError(NodeError):
    pass

class CircularDagError(NodeError):
    pass


