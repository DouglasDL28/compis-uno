import time
from typing import Tuple

from automata.FiniteAutomata import FiniteAutomata


class DFA(FiniteAutomata):
    """ Deterministic Finite Automata. Inherits from FiniteAutomata. """


    def move(self, s, c):
        """ Move from state s with character c defined in ∂. """

        try:
            return self.delta[s][c]
        except:
            pass

    def simulate(self, word) -> Tuple[bool, float]:
        start_t = time.time()
        s = self.q_init
        for c in word:
            s = self.move(s, c)
        
        if s in self.F:
            end_t = time.time()
            return True, (end_t - start_t)

        end_t = time.time()
        return False, (end_t - start_t)

    pass

if __name__ == "__main__":
    dfa = DFA(Q=[], Sigma=[], delta=[], q_init="a", F=[])
    print(dfa)