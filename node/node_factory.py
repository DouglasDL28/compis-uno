import operators as op

from .node import PlusNode
from .node import KleeneNode
from .node import ConcatNode
from .node import OptionalNode
from .node import OrNode


class OperatorNodeFactory():
    def get_node(self, operator: op.Operators, left=None, right=None, position=None, thompson=False, direct=False, followpos=[]):
        if operator is None:
            return None

        elif operator == op.Operators.KLEENE:
            return KleeneNode(
                value=operator,
                left=left,
                position=position,
                thompson=thompson,
                direct=direct,
                followpos=followpos
            )

        elif operator == op.Operators.CONCAT:
            return ConcatNode(
                value=operator,
                left=left,
                right=right,
                position=position,
                thompson=thompson,
                direct=direct,
                followpos=followpos
            )

        elif operator == op.Operators.OPTIONAL:
            return OptionalNode(
                value=operator,
                left=left,
                position=position,
                thompson=thompson,
                direct=direct,
                followpos=followpos
            )

        elif operator == op.Operators.OR:
            return OrNode(
                value=operator,
                left=left,
                right=right,
                position=position,
                thompson=thompson,
                direct=direct,
                followpos=followpos
            )

        elif operator == op.Operators.PLUS:
            return PlusNode(
                value=operator,
                left=left,
                position=position,
                thompson=thompson,
                direct=direct,
                followpos=followpos
            )

        else:
            return None
