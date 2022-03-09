from re import T
from automata.FiniteAutomata import FiniteAutomata
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

        posfix = []
        stack = Stack()
        prev = ""
        for c in re:
            if c in self.alphabet: # operand
                if prev in self.alphabet or prev == '*' or prev == ')': # CONCAT operator
                    op = Operators.CONCAT
                    while (not stack.empty()) and (PRECEDENCE[op] <= PRECEDENCE[stack.peek()]):
                        posfix.append(stack.pop()) 
                    stack.push(op)

                posfix.append(c)

            elif c in OPERATORS.keys():
                if c == '(':
                    if prev in self.alphabet or prev == '*' or prev == ')': # CONCAT operator
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
        return posfix

    def Thompson(self, re):
        """ Generate NFA from regular expression. Generates expression tree. """

        re = self.infix_to_posfix(re)

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
        self.alphabet.add("#")
        re = self.infix_to_posfix(re + "#")
        
        stack = Stack()
        op_node_factory = OperatorNodeFactory()

        followpos = []
        
        position = 0
        for c in re:
            if c in self.alphabet:  # operand
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
        tree = stack.pop()
        self.tree = tree

        return tree

    def __str__(self) -> str:
        return f"""\
∑: {self.alphabet}
FA: {self.FA}
"""
    

if __name__ == '__main__':
    test_re = "(a|b)*abb"
    word = "aaaabb"
    re = RegularExpression(test_re)
    print("test_re:", test_re)

    tree = re.direct_construction(test_re)
    tree.print_tree(tree)
    # re.Thompson(test_re)

    # print(re.tree.print_tree(re.tree))

    # dfa = re.thompson_nfa.subset_construction()
    # dfa.plot("SubsetConstruction.png", True)

    # val, time = re.thompson_nfa.simulate(word)
    # print("Thompson NFA:",  val)
    
    # val, time = dfa.simulate(word)
    # print("Subsets DFA:", val)
