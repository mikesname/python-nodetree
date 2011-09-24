"""
Nodetree test nodes.
"""

from __future__ import absolute_import

import types

from . import node, decorators


@decorators.makenode(types.IntType, types.IntType)
def add_five(input):
    return input + 5


class Number(node.Node):
    """A number constant."""
    intypes = []
    outtype = types.IntType
    parameters = [
            dict(name="num", value=0),
    ]

    def process(self):
        return self._params.get("num")


class Arithmetic(node.Node):
    """Operate on two numbers"""
    intypes = [types.IntType, types.IntType]
    outtype = types.IntType
    parameters = [
        dict(name="operator", value="+", choices=[
            "+", "-", "*", "/",    
        ]),
    ]

    def process(self, lhs, rhs):
        op = self._params.get("operator")
        if op == "+":
            return lhs + rhs
        elif op == "-":
            return lhs - rhs
        elif op == "*":
            return lhs * rhs
        elif op == "/":
            return lhs / rhs


