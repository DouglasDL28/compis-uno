import time
from typing import Tuple

from automata.DFA import DFA
from automata.NFA import NFA
from node.node import Node
from node.node import SymbolNode
from Stack import Stack
from node.node_factory import OperatorNodeFactory
from operators import Operators, OPERATORS, PRECEDENCE, UNARY_OPS

    

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
        """ Returns regular expression in postfix format. """

        operators = OPERATORS.keys()
        parenthesis_count = 0
        postfix = []
        stack = Stack()
        prev = ""
        for c in re:
            if c in self.alphabet: # operand
                if (prev in self.alphabet) or (prev in UNARY_OPS) or (prev == ')'): # CONCAT operator
                    op = Operators.CONCAT
                    while (not stack.empty()) and (PRECEDENCE[op] <= PRECEDENCE[stack.peek()]):
                        postfix.append(stack.pop()) 
                    stack.push(op)

                postfix.append(c)

            elif c in operators:
                if c == '(':
                    parenthesis_count += 1
                    if (prev in self.alphabet) or (prev in UNARY_OPS) or (prev == ')'): # CONCAT operator
                        op = Operators.CONCAT
                        while (not stack.empty()) and (PRECEDENCE[op] <= PRECEDENCE[stack.peek()]):
                            postfix.append(stack.pop())
                        stack.push(op)

                    stack.push(OPERATORS[c])
                
                elif c == ')':
                    parenthesis_count -= 1
                    while ( (not stack.empty()) and (stack.peek() != OPERATORS['('])):
                        a = stack.pop()
                        postfix.append(a)
                    if ((not stack.empty()) and (stack.peek() != OPERATORS['('])):
                        return -1
                    else:
                        stack.pop()
                
                else: # operator
                    op = OPERATORS[c]
                    while not stack.empty() and PRECEDENCE[op] <= PRECEDENCE[stack.peek()]:
                        postfix.append(stack.pop())
                    stack.push(op)
            
            prev = c

        # Validate parenthesis count in regular expression.
        if parenthesis_count < 0:
            raise Exception("Too many closing parenthesis ')' in regular expression.")
        elif parenthesis_count > 0:
            raise Exception("Too many open parenthesis '(' in regular expression.")
        
        while not stack.empty():
            postfix.append(stack.pop())

        self.postfix = postfix

        return postfix

    def Thompson(self) -> Tuple[Node, float]:
        """ Generate NFA from regular expression. Generates expression tree. """

        start_t = time.time()

        re = self.infix_to_posfix(self.re)

        stack = Stack()
        op_node_factory = OperatorNodeFactory()

        for c in re:
            if c in self.alphabet:  # operand
                stack.push(SymbolNode(value=c, thompson=True))

            else: # operators
                if c.value in UNARY_OPS:
                    if not stack.empty():
                        left = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")

                    node = op_node_factory.get_node(c, left, thompson=True)
                    stack.push(node)

                else:
                    if not stack.empty():
                        right = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")
                    
                    if not stack.empty():
                        left = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")

                    node = op_node_factory.get_node(c, left, right, thompson=True)
                    stack.push(node)


        tree = stack.pop()
        tree.fa.Sigma = self.alphabet
        self.tree = tree

        self.thompson_nfa = tree.fa

        end_t = time.time()

        return tree, (end_t - start_t)

    def direct_construction(self, tokens: dict, keywords: dict, except_keyword: dict) -> Tuple[DFA, float]:

        start_t = time.time()

        re = self.infix_to_posfix(self.re)
        
        stack = Stack()
        op_node_factory = OperatorNodeFactory()

        followpos = []
        symbol_pos_map = {a : set() for a in self.alphabet}
        tokens_pos = {}

        token_idx = 0
        position = 0
        for c in re:
            if c == '#': # token end symbol
                symbol_pos_map[c].add(position)
                tokens_pos[position] = token_idx
                token_idx += 1
                followpos.append(set())
                stack.push(SymbolNode(value=c, position=position, direct=True, followpos=followpos))
                position += 1


            elif c in self.alphabet:  # operand
                symbol_pos_map[c].add(position)
                followpos.append(set())
                stack.push(SymbolNode(value=c, position=position, direct=True, followpos=followpos))
                position += 1

            else: # operators
                if c.value in UNARY_OPS:
                    if not stack.empty():
                        left = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")
                    
                    node = op_node_factory.get_node(c, left, direct=True, followpos=followpos)

                    stack.push(node)

                else:
                    if not stack.empty():
                        right = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")
                    
                    if not stack.empty():
                        left = stack.pop()
                    else:
                        raise Exception(f"Not a valid regular expression. Missing operands for {c.value} operator.")

                    node = op_node_factory.get_node(c, left, right, direct=True, followpos=followpos)

                    stack.push(node)

        tree: Node = stack.pop()

        print("tokens:", tokens_pos)

        # tree.print_tree(tree)

        D_states: set = set()
        D_tran = {}
        F = set()

        stack = Stack()

        self.alphabet.remove('#')

        # print("root firstpos: \n", tree.firstpos())
        # print("followpos: \n", followpos)

        q_init = tuple(tree.firstpos())
        D_states.add(q_init)
        stack.push(q_init)

        # print("sybol_pos_map: \n", json.dumps(symbol_pos_map, indent=2, default=str))

        token_states = [set() for i in range(len(tokens))] # array of states sets

        while not stack.empty():
            S = stack.pop()
            D_tran[S] = {}

            for a in self.alphabet:
                U = set()
                for p in S:
                    if p in symbol_pos_map[a]:
                        U = U.union(followpos[p])

                temp_U = U
                U = tuple(U)
    
                if U:
                    if U not in D_states: # Add new states
                        D_states.add(U)
                        stack.push(U)
                        
                        terminals = symbol_pos_map['#'].intersection(temp_U)

                        if terminals: # check if empty
                            for pos in terminals:
                                idx = tokens_pos[pos]
                                token_states[idx].add(U) # add state to token states

                            F.add(U)

                    D_tran[S][a] = U

        end_t = time.time()

        return (
            DFA(
                Q=D_states,
                Sigma=self.alphabet,
                delta=D_tran,
                q_init=q_init,
                F=F,
                tokens=tokens,
                token_states=token_states,
                keywords=keywords,
                except_keyword=except_keyword
            ),
            end_t - start_t
        )
        

    def __str__(self) -> str:
        return f"""\
∑: {self.alphabet}
FA: {self.FA}
"""
    

if __name__ == '__main__':
    direct = True
    subset = True
    test_re = "(0|1)1*(0|1)"
    word = "0011111"
    re = RegularExpression(test_re)
    print("regular expression:", test_re)

    # Thompson
    print("--------THOMPSON--------")
    thompson, thompson_elapsed = re.Thompson()
    print("Thompson elapsed time: ", thompson_elapsed)
    thompson.plot_fa("Thompson.png")

    sim, elapsed = thompson.fa.simulate(word)
    print(f"Thompson NFA simulation: {sim} -- elapsed time: {elapsed}\n")
    
    # Subset
    print("--------SUBSETS--------")
    subset_dfa, elapsed_t = re.thompson_nfa.subset_construction()
    print("Subset construction elapsed time: ", elapsed_t)

    subset_dfa.plot("SubsetConstruction.png")

    sim, elapsed_t  = subset_dfa.simulate(word)
    print(f"Subset DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")

    # Direct
    print("--------DIRECT--------")
    dfa, elapsed_t = re.direct_construction()
    print("Direct Construction elapsed time: ", elapsed_t)

    dfa.plot("Directo.png")

    sim, elapsed_t  = subset_dfa.simulate(word)
    print(f"Direct Construction DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")
