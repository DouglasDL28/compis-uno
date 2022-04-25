import time
from typing import Tuple

from automata.FiniteAutomata import FiniteAutomata


class DFA(FiniteAutomata):
    """ Deterministic Finite Automata. Inherits from FiniteAutomata. """

    def __init__(
        self,
        Q: set = ...,
        Sigma: set = ...,
        delta: dict = ...,
        q_init=None,
        F: set = ...,
        tokens: dict = {},
        token_states: list = [],
        keywords: list = [],
        except_keyword: dict = {},
    ) -> None:
        super().__init__(Q, Sigma, delta, q_init, F)
        
        self.tokens = tokens
        self.token_states = token_states
        self.keywords = keywords
        self.except_keyword = except_keyword


    def move(self, s, c):
        """ Move from state s with character c defined in ∂. """

        try:
            return self.delta[s][c]
        except:
            return None

    def simulate(self, filename = None) -> Tuple[bool, float]:

        # TODO defensive programming
        file = open(filename, 'r').read()
        file_len = len(file)

        tokens = []

        start_t = time.time()

        current_token = None
        lexeme = ""

        s = self.q_init
        i = 0

        while (i <= file_len - 1):

            s = self.move(s, file[i])
        
            if s in self.F: # terminal
                lexeme += file[i]

                # find first token that matches
                for j, states in enumerate(self.token_states):
                    if s in states:
                        token = list(self.tokens)[j]
                        if (token in self.except_keyword) and (lexeme in self.keywords):
                            current_token = (lexeme, lexeme) # keyword
                        else:
                            current_token = (token, lexeme) # token

                        break

                if i == (file_len - 1): # eof
                    tokens.append(current_token)

                elif not self.move(s, file[i+1]): # no transition
                    lexeme = ""
                    tokens.append(current_token)
                    s = self.q_init # restart dfa
                
                i += 1

            else: # no terminal
                # no transition or eof
                if i == (file_len - 1) and not self.move(s, file[i+1]):
                    raise Exception("Lexical error.")

                else:
                    lexeme += file[i]
                    i += 1

        print("eof")


            
        print(*tokens, sep='\n')

        end_t = time.time()
        return True, (end_t - start_t)

    pass

if __name__ == "__main__":
    dfa = DFA(Q=[], Sigma=[], delta=[], q_init="a", F=[])
    print(dfa)
