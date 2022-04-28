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
        token_names: list = [],
        token_states: list = [],
        keywords: dict = {},
        except_keyword: dict = {},
        ignore: set = set(),
    ) -> None:
        super().__init__(Q, Sigma, delta, q_init, F)
        
        self.token_names = token_names
        self.token_states = token_states
        self.keywords = keywords
        self.except_keyword = except_keyword
        self.ignore = ignore

    def get_keywords_set(self):
        kwrds = set()
        for kwrd in self.keywords:
            lexeme = ''.join(chr(c) for c in self.keywords[kwrd])
            kwrds.add(lexeme)

        return kwrds

    def move(self, s, c):
        """ Move from state s with character c defined in ∂. """

        try:
            return self.delta[s][c]
        except:
            return None

    def simulate(self, filename=None) -> Tuple[bool, float]:

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
            
            # IGNORE SET
            if ord(file[i]) in self.ignore:
                i += 1
                continue

            s = self.move(s, ord(file[i]))
        
            if s in self.F: # terminal
                lexeme += file[i]

                # find first token that matches
                for j, states in enumerate(self.token_states):
                    if s in states:
                        token = self.token_names[j]
                        if (token in self.except_keyword
                            and lexeme in self.get_keywords_set()):
                            current_token = (lexeme, lexeme) # keyword
                        else:
                            current_token = (token, lexeme) # token

                        break

                if i == (file_len - 1): # eof
                    tokens.append(current_token)

                elif not self.move(s, ord(file[i+1])): # no transition
                    lexeme = ""
                    tokens.append(current_token)
                    s = self.q_init # restart dfa
                
                i += 1

            else: # no terminal
                # no transition or eof
                if i == (file_len - 1) or not self.move(s, ord(file[i+1])):
                    print("Lexical error.", file[i])
                    i += 1
                    s = self.q_init # restart dfa

                else:
                    lexeme += file[i]
                    i += 1

        print("eof")

        print(*tokens, sep='\n')

        end_t = time.time()
        return True, (end_t - start_t)

if __name__ == "__main__":
    dfa = DFA(Q=[], Sigma=[], delta=[], q_init="a", F=[])
    print(dfa)
