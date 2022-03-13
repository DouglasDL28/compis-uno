from automata.NFA import FiniteAutomata, NFA
from operators import Operators


thompson_q = 0


def get_state():
    global thompson_q
    state = thompson_q
    thompson_q += 1
    return state


class Node:
    """ Build expression tree. """

    def __init__(self, value=None, left=None, right=None, position=None, thompson=False, direct=False, followpos: list = []) -> None:
        self.value = value
        self.right: Node = right
        self.left: Node = left

        if thompson:
            self.fa: FiniteAutomata = self.thompson()
        if direct:
            self.position: int = position
            self.firstpos()
            self.lastpos()
            self.followpos(followpos)

    def postorder(self, root):
        if root:
            # Traverse left
            self.postorder(root.left)
            # Traverse right
            self.postorder(root.right)
            # Traverse root
            print(str(root) + " ", end='')

    def print_tree(self, node, level=0):
        if node != None:
            self.print_tree(node.left, level + 1)
            print(' ' * 4 * level + '-> ' + str(node))
            self.print_tree(node.right, level + 1)

    def thompson(self,):
        pass

    def plot_fa(self, output_file, show=False):
        self.fa.plot(output_file, show)

    def nullable(self) -> bool:
        pass

    def firstpos(self) -> set:
        pass

    def lastpos(self) -> set:
        pass

    def followpos(self, arr: list):
        pass

    def __str__(self) -> str:
        val = self.value.value if isinstance(self.value, Operators) else self.value
        # position = f" ({self.position})" if self.position else ""
        res = f"{val}"
        return res


#Symbol, Concat, Plus, Optional, Or, Kleene
class SymbolNode(Node):
    def thompson(self):
        q_init = get_state()
        F = get_state()

        self.fa = NFA(
            Q={q_init, F},
            delta={
                q_init: {self.value: [F]}
            },
            q_init=q_init,
            F={F},
        )

        return self.fa

    def nullable(self) -> bool:
        if self.value == 'ε':
            return True
        elif self.position is not None:
            return False

    def firstpos(self) -> set:
        if self.value == 'ε':
            return set()
        elif self.position is not None:
            return {self.position}

    def lastpos(self) -> set:
        if self.value == 'ε':
            return set()
        elif self.position is not None:
            return {self.position}

    def followpos(self, arr: list):
        pass


class OrNode(Node):
    def thompson(self,):
        left = self.left.fa
        right = self.right.fa

        q_init = get_state()
        F = get_state()

        Q = right.Q.union(left.Q)
        Q.add(q_init)
        Q.add(F)

        delta = {**left.delta, **right.delta}
        delta[q_init] = {'ε': [right.q_init, left.q_init]}
        delta[next(iter(right.F))] = {'ε': [F]}
        delta[next(iter(left.F))] = {'ε': [F]}

        self.fa = NFA(
            Q=Q,
            delta=delta,
            q_init=q_init,
            F={F}
        )

        return self.fa

    def nullable(self) -> bool:
        return self.left.nullable() or self.right.nullable()

    def firstpos(self) -> set:
        return self.left.firstpos().union(self.right.firstpos())

    def lastpos(self) -> set:
        return self.left.lastpos().union(self.right.lastpos())

    def followpos(self, arr: list):
        pass


class ConcatNode(Node):
    def thompson(self,):
        right = self.right.fa
        left = self.left.fa

        Q = right.Q.union(left.Q)

        delta = {**right.delta, **left.delta}
        delta[next(iter(left.F))] = {'ε': [right.q_init]}

        self.fa = NFA(
            Q=Q,
            delta=delta,
            q_init=left.q_init,
            F=right.F
        )

        return self.fa

    def nullable(self) -> bool:
        return self.left.nullable() and self.right.nullable()

    def firstpos(self) -> set:
        if self.left.nullable():
            return self.left.firstpos().union(self.right.firstpos())
        else:
            return self.left.firstpos()

    def lastpos(self) -> set:
        if self.right.nullable():
            return self.left.lastpos().union(self.right.lastpos())
        else:
            return self.right.lastpos()

    def followpos(self, arr: list):
        for i in self.left.lastpos():
            arr[i] = arr[i].union(self.right.firstpos())
        pass


class KleeneNode(Node):
    def thompson(self,):
        left = self.left.fa

        q_init = get_state()
        F = get_state()

        Q = left.Q
        Q.add(q_init)
        Q.add(F)

        delta = left.delta
        delta[q_init] = {'ε': [left.q_init, F]}
        delta[next(iter(left.F))] = {'ε': [left.q_init, F]}

        self.fa = NFA(
            Q=Q,
            delta=delta,
            q_init=q_init,
            F={F}
        )

        return self.fa

    def nullable(self) -> bool:
        return True

    def firstpos(self) -> set:
        return self.left.firstpos()

    def lastpos(self) -> set:
        return self.left.lastpos()

    def followpos(self, arr: list):
        for i in self.lastpos():
            arr[i] = arr[i].union(self.firstpos())


class OptionalNode(Node):
    """ (a|b) """

    def thompson(self):
        left = self.left.fa

        q_init = get_state()
        F = get_state()

        Q = left.Q
        Q.add(q_init)
        Q.add(F)

        delta = left.delta
        delta[q_init] = {'ε': [left.q_init, F]}
        delta[next(iter(left.F))] = {'ε': [F]}

        self.fa = NFA(
            Q=Q,
            delta=delta,
            q_init=q_init,
            F={F}
        )

        return self.fa

    def nullable(self):
        return True

    def firstpos(self):
        return self.left.firstpos()

    def lastpos(self):
        return self.left.lastpos()

    def followpos(self, arr: list):
        pass


class PlusNode(Node):
    def thompson(self,):
        left = self.left.fa

        q_init = get_state()
        F = get_state()

        Q = left.Q
        Q.add(q_init)
        Q.add(F)

        delta = left.delta
        delta[q_init] = {'ε': [left.q_init]}
        delta[next(iter(left.F))] = {'ε': [left.q_init, F]}

        self.fa = NFA(
            Q=Q,
            delta=delta,
            q_init=q_init,
            F={F}
        )

        return self.fa

    def nullable(self) -> bool:
        return self.left.nullable()

    def firstpos(self) -> set:
        return self.left.firstpos()

    def lastpos(self) -> set:
        return self.left.lastpos()

    def followpos(self, arr: list):
        for i in self.lastpos():
            arr[i] = arr[i].union(self.firstpos())


if __name__ == "__main__":
    concat_node = ConcatNode(
        value=Operators.CONCAT,
        left=SymbolNode(value='a', thompson=True),
        right=SymbolNode(value='b', thompson=True),
        thompson=True
    )
    concat_node.plot_fa("concatNFA.png", False)

    kleene_node = KleeneNode(
        value=Operators.KLEENE,
        left=SymbolNode(value='a', thompson=True),
        thompson=True
    )
    kleene_node.plot_fa("kleeneNFA.png", False)

    optional_node = OptionalNode(
        value=Operators.OPTIONAL,
        left=SymbolNode(value='a', thompson=True),
        thompson=True
    )
    optional_node.plot_fa("optionalNFA.png", False)

    or_node = OrNode(
        value=Operators.OR,
        left=SymbolNode(value='a', thompson=True),
        right=SymbolNode(value='b', thompson=True),
        thompson=True
    )
    or_node.plot_fa("orNFA.png", False)

    plus_node = PlusNode(
        value=Operators.PLUS,
        left=SymbolNode(value='a', thompson=True),
        thompson=True
    )
    plus_node.plot_fa("plusNFA.png", False)

    symbol_node = SymbolNode(value='a', thompson=True)
    symbol_node.plot_fa("symbolNFA.png", False)
