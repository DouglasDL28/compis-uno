from automata.DFA import DFA
from automata.NFA import NFA
from node.node import KleeneNode, Node, OptionalNode, PlusNode
from node.node import SymbolNode
from Stack import Stack
from node.node_factory import OperatorNodeFactory
from operators import Operators, OPERATORS, PRECEDENCE

    

class RegularExpression:

    def __init__(self, re) -> None:
        self.re = re
        self.alphabet: set = self.generate_alphabet(re)
        self.tree: Node = None
        self.thompson_nfa: NFA = None

    def generate_alphabet(self, re) -> set:
        """ Generates alphabet given a regular expression. """

        alphabet = set(re)

        # Remove operators from set
        for op in OPERATORS.keys():
            alphabet.discard(op)

        return alphabet

    def infix_to_posfix(self, re):
        """ Returns regular expression in posfix format. """

        unaryops = {"+", "*", "?"}
        operators = OPERATORS.keys()
        
        posfix = []
        stack = Stack()
        prev = ""
        for c in re:
            if c in self.alphabet: # operand
                if (prev in self.alphabet) or (prev in unaryops) or (prev == ')'): # CONCAT operator
                    op = Operators.CONCAT
                    while (not stack.empty()) and (PRECEDENCE[op] <= PRECEDENCE[stack.peek()]):
                        posfix.append(stack.pop()) 
                    stack.push(op)

                posfix.append(c)

            elif c in operators:
                if c == '(':
                    if (prev in self.alphabet) or (prev in unaryops) or (prev == ')'): # CONCAT operator
                        op = Operators.CONCAT
                        while (not stack.empty()) and (PRECEDENCE[op] <= PRECEDENCE[stack.peek()]):
                            posfix.append(stack.pop())
                        stack.push(op)

                    stack.push(OPERATORS[c])
                
                elif c == ')':
                    while ( (not stack.empty()) and (stack.peek() != OPERATORS['('])):
                        a = stack.pop()
                        posfix.append(a)
                    if ((not stack.empty()) and (stack.peek() != OPERATORS['('])):
                        return -1
                    else:
                        stack.pop()
                
                else: # operator
                    op = OPERATORS[c]
                    while not stack.empty() and PRECEDENCE[op] <= PRECEDENCE[stack.peek()]:
                        posfix.append(stack.pop())
                    stack.push(op)
            
            prev = c
        
        while not stack.empty():
            posfix.append(stack.pop())

        self.posfix = posfix

        for c in posfix:
            if isinstance(c, Operators):
                print(c.value, end=" ")
            else:
                print(c, end=" ")
        print()

        return posfix

    def Thompson(self, re):
        """ Generate NFA from regular expression. Generates expression tree. """

        re = self.infix_to_posfix(re)
        print("postfix re:", re)

        stack = Stack()
        op_node_factory = OperatorNodeFactory()

        for c in re:
            if c in self.alphabet:  # operand
                stack.push(SymbolNode(value=c, thompson=True))

            else: # operators
                if c == Operators.KLEENE:
                    stack.push(KleeneNode(value=c, left=stack.pop(), thompson=True))
                elif c == Operators.PLUS:
                    stack.push(PlusNode(value=c, left=stack.pop(), thompson=True))
                elif c == Operators.OPTIONAL:
                    stack.push(PlusNode(value=c, left=stack.pop(), thompson=True))
                else:
                    right = stack.pop()
                    left = stack.pop()
                    node = op_node_factory.get_node(c, left, right, thompson=True)

                    stack.push(node)

        tree = stack.pop()
        tree.fa.Sigma = self.alphabet
        self.tree = tree
        self.tree.plot_fa("Thompson.png")

        self.thompson_nfa = tree.fa

        return tree

    def direct_construction(self, re):
        print("alfabeto:", self.alphabet)
        self.alphabet.add("#")
        re = self.infix_to_posfix(re + "#")
        
        stack = Stack()
        op_node_factory = OperatorNodeFactory()

        followpos = []
        symbol_pos_map = {a : set() for a in self.alphabet}
        
        position = 0
        for c in re:
            if c in self.alphabet:  # operand
                symbol_pos_map[c].add(position)
                followpos.append(set())
                stack.push(SymbolNode(value=c, position=position, direct=True, followpos=followpos))
                position += 1

            else: # operators
                if c == Operators.KLEENE:
                    stack.push(KleeneNode(value=c, left=stack.pop(), direct=True, followpos=followpos))
                elif c == Operators.PLUS:
                    stack.push(PlusNode(value=c, left=stack.pop(), direct=True, followpos=followpos))
                elif c == Operators.OPTIONAL:
                    stack.push(OptionalNode(value=c, left=stack.pop(), direct=True, followpos=followpos))
                else:
                    right = stack.pop()
                    left = stack.pop()
                    node = op_node_factory.get_node(c, left, right, direct=True, followpos=followpos)

                    stack.push(node)

        print(followpos)
        tree: Node = stack.pop()

        # tree.print_tree(tree)

        D_states: set = set()
        D_tran = {}
        F = set()

        stack = Stack()

        self.alphabet.remove('#')

        q_init = tuple(tree.firstpos())
        print("q_init:", q_init)
        D_states.add(q_init)
        stack.push(q_init)

        while not stack.empty():
            S = stack.pop()
            D_tran[S] = {}

            is_terminal = False
            for a in self.alphabet:
                U = set()
                for p in S:
                    if p in symbol_pos_map[a]:
                        U = U.union(followpos[p])
                    if p in symbol_pos_map["#"]:
                        is_terminal = True

                U = tuple(U)
                if U:
                    if U not in D_states: # Add new states
                        D_states.add(U)
                        stack.push(U)
                            
                        if is_terminal: # Terminals
                            F.add(U)

                    D_tran[S][a] = U

        return DFA(
            Q=D_states,
            Sigma=self.alphabet,
            delta=D_tran,
            q_init=q_init,
            F=F
        )

    def __str__(self) -> str:
        return f"""\
∑: {self.alphabet}
FA: {self.FA}
"""
    

if __name__ == '__main__':
    direct = True
    subset = False
    test_re = "(a|b)*((a|(bb))*ε)"
    word = "abaabbabaa"
    re = RegularExpression(test_re)
    print("test_re:", test_re)

    if direct:
        tree = re.direct_construction(test_re)
        # tree.print_tree(tree)
        tree.plot("Directo.png")

    if subset:
        # Thompson
        re.Thompson(test_re)
        print(re.tree.print_tree(re.tree))

        subset_dfa = re.thompson_nfa.subset_construction()
        subset_dfa.plot("SubsetConstruction.png", False)



    # val, time = re.thompson_nfa.simulate(word)
    # print("Thompson NFA:",  val)
    
    # val, time = dfa.simulate(word)
    # print("Subsets DFA:", val)
