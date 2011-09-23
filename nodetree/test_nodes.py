"""
Nodetree test nodes.
"""

from __future__ import absolute_import

import types

from . import node


class Number(node.Node):
    """A number constant."""
    intypes = []
    outtype = types.IntType
    parameters = [
            dict(name="num", value=0),
    ]

    def _eval(self):
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

    def _eval(self):
        op = self._params.get("operator")
        lhs = self.eval_input(0)
        rhs = self.eval_input(1)
        if op == "+":
            return lhs + rhs
        elif op == "-":
            return lhs - rhs
        elif op == "*":
            return lhs * rhs
        elif op == "/":
            return lhs / rhs


