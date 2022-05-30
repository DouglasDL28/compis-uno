import time
from typing import Tuple

from automata.FiniteAutomata import FiniteAutomata

class Token():
    def __init__(self, name, lexeme) -> None:
        self.name: str = name
        self.lexeme: str = lexeme

    def __str__(self) -> str:
        return f"<{self.name}, '{self.lexeme}'>"

class Scanner(FiniteAutomata):
    """ Deterministic Finite Automata. Inherits from FiniteAutomata. """

    def __init__(self,) -> None:
        self.Q = {(73,), (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), (79,), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 64, 65, 70, 72, 74, 76, 78, 80, 82, 84, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 63), (85,), (75,), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), (42, 43, 44, 45, 46, 47, 48, 49, 50, 51), (81,), (71,), (66, 67, 68, 69), (77,), (83,)}
        self.Sigma = {9, 10, 13, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59}
        self.delta = {(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 64, 65, 70, 72, 74, 76, 78, 80, 82, 84, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 63): {9: (66, 67, 68, 69), 10: (66, 67, 68, 69), 13: (66, 67, 68, 69), 40: (83,), 41: (85,), 42: (79,), 43: (75,), 45: (77,), 46: (73,), 47: (81,), 48: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 49: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 50: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 51: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 52: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 53: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 54: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 55: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 56: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 57: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 59: (71,)}, (71,): {}, (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41): {46: (42, 43, 44, 45, 46, 47, 48, 49, 50, 51), 48: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 49: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 50: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 51: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 52: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 53: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 54: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 55: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 56: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), 57: (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41)}, (42, 43, 44, 45, 46, 47, 48, 49, 50, 51): {48: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 49: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 50: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 51: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 52: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 53: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 54: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 55: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 56: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 57: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)}, (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62): {48: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 49: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 50: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 51: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 52: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 53: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 54: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 55: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 56: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), 57: (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)}, (81,): {}, (73,): {}, (77,): {}, (75,): {}, (79,): {}, (85,): {}, (83,): {}, (66, 67, 68, 69): {9: (66, 67, 68, 69), 10: (66, 67, 68, 69), 13: (66, 67, 68, 69)}}
        self.q_init = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 64, 65, 70, 72, 74, 76, 78, 80, 82, 84, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 63)
        self.F = {(73,), (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62), (79,), (85,), (75,), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41), (81,), (71,), (66, 67, 68, 69), (77,), (83,)}
        self.token_names = ['number', 'decnumber', 'white', ';', '.', '+', '-', '*', '/', '(', ')']
        self.token_states = [{(10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41)}, {(52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)}, {(66, 67, 68, 69)}, {(71,)}, {(73,)}, {(75,)}, {(77,)}, {(79,)}, {(81,)}, {(83,)}, {(85,)}]
        self.keywords = {}
        self.except_keyword = {}
        self.ignore = set()

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
                            current_token = Token(lexeme, lexeme) # keyword
                        else:
                            current_token = Token(token, lexeme) # token
                        
                        last_idx = i

                        break

                if i == (file_len - 1): # eof
                    tokens.append(current_token)
                    # print(current_token)
                    current_token = None

                elif not self.move(s, ord(file[i+1])): # no transition
                    lexeme = ""
                    tokens.append(current_token)
                    # print(current_token)
                    current_token = None
                    s = self.q_init # restart dfa
                
                i += 1

            else: # no terminal
                # no transition or eof
                if i == (file_len - 1) or not self.move(s, ord(file[i+1])):
                    print("Lexical error.", file[i])
                    if current_token:
                        tokens.append(current_token)
                        # print(current_token)
                        current_token = None
                    lexeme = "" # empty buffer
                    s = self.q_init # restart dfa
                    i = last_idx + 1

                else: 
                    lexeme += file[i]
                    i += 1

        end_t = time.time()
        return True, tokens, (end_t - start_t)


if __name__ == "__main__":
    dfa = Scanner()

    filename = input("Input filename: ") or "tests/test.txt"

    sim, tokens, elapsed_t  = dfa.simulate(filename=filename)
    print(f"Direct Construction DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")

    print(*tokens, sep='\n')
