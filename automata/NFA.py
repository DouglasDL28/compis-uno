import time
from tracemalloc import start

from typing import Tuple
from Stack import Stack

from automata.FiniteAutomata import FiniteAutomata
from automata.DFA import DFA


class NFA(FiniteAutomata):
    """ Deterministic Finite Automata. Inherits from FiniteAutomata. """

    def epsilon_closure(self, T, res:set=set()) -> set:
        """
        If T is a set, returns set of NFA states reachable from some NFA state s in set T on epsilon-transition alone.
        If T is a symbol, returns set of NFA states reachable from NFA state s on epsilon-transition alone.
        """
        if isinstance(T, set):
            res = res.union(T)
            for s in T:
                self.epsilon_closure(s, res)

            return res
        else: # symbol
            s = T
            if s in self.delta.keys() and 'ε' in self.delta[s].keys():
                for state in self.delta[s]['ε']:
                    res.add(state)
                    self.epsilon_closure(state, res)
        
        return res

    def closure_s(self, s, res:set=set()):
        return

    def move(self, T, a) -> set:
        """ Set of NFA states to which there is a transition on input symbol a from some state s in T. """

        res: set = set()
        for state in T:
            if state in self.delta.keys() and a in self.delta[state].keys():
                for q in self.delta[state][a]:
                    res.add(q)

        return res

    def simulate(self, word) -> Tuple[bool, float]:
        start_t = time.time()
        S = self.epsilon_closure(self.q_init, res=set())
        
        for c in word:
            S = self.epsilon_closure(self.move(S, c), res=set())
        
        if len(S.intersection(self.F)) > 0:
            end_t = time.time()
            return True, (end_t - start_t)
        else:
            end_t = time.time()
            return False, (end_t - start_t)

    def subset_construction(self,) -> Tuple[DFA, float]:

        start_t = time.time()

        D_states: set = set()
        D_tran = {}
        F = set()

        stack = Stack()

        q_init = tuple(self.epsilon_closure(self.q_init))
        D_states.add(q_init)
        stack.push(q_init)

        self.Sigma.discard('ε')
        print("sigma:", self.Sigma)

        while not stack.empty():
            T = stack.pop()
            D_tran[T] = {}
            for a in self.Sigma:
                move = self.move(T, a)
                U = tuple(self.epsilon_closure(move, res=set()))
                if U:
                    if U not in D_states: # Add new states
                        D_states.add(U)
                        stack.push(U)
                        
                        if len(self.F.intersection(U)) > 0: # Terminals
                            F.add(U)
    
                    D_tran[T][a] = U

        self.Sigma.add('ε')
        end_t = time.time()

        return (
            DFA(
                Q=D_states,
                Sigma=self.Sigma,
                delta=D_tran,
                q_init=q_init,
                F=F
            ),
            (end_t - start_t)
        )
        



if __name__ == "__main__":
    nfa = NFA([], [], [], "a", [])
    print(nfa)
