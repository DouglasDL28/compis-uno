import re

from Stack import Stack


SPECIFICATIONS = ["COMPILER", "CHARACTERS", "KEYWORDS", "TOKENS", "PRODUCTIONS", "END"]

class Scanner:
    """ CoCoL parser """

    compiler: str = ""
    characters: dict = {}
    keywords: dict = {}
    tokens: dict = {}
    productions: dict = {}

    index = 0
    line = 1

    def __init__(self, filename) -> None:
        self.filename = filename

    def scan(self, filename = None):
        """ Parse COCOl filename. """

        filename = filename if filename else self.filename
        file = open(filename, "r").read()
        self.index = 0
        self.line = 1

        def peek(offset = 1) -> str:
            return file[self.index + offset]

        def peek_word():
            word = ""
            temp_index = self.index
            while True:
                char = file[temp_index]

                if word != "" and char in {" ", "\t", "\n"}:
                    break
                elif word == "" and char in {" ", "\t", "\n"}:
                    temp_index += 1
                else:
                    word += char
                    temp_index += 1

            return word

        def increment_index(offset = 1):
            self.index += offset

        def scan_comment():
            increment_index(2)
            comment = ""
            while file[self.index] != "." and peek() != ')':
                comment += file[self.index]
                increment_index()
            increment_index(2)
        
        def expect(word) -> bool:
            """ Read expected word from file. """

            word_pos = 0
            matches = True

            while True:
                char = file[self.index]

                if char in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif char == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif char == '(' and peek() == '.': # comments
                    scan_comment()
                
                else:
                    if char == word[word_pos]:
                        increment_index()
                        word_pos += 1
                        matches = True
                    else:
                        return False
                
                if word_pos == len(word):
                    return matches
            
        def scan_compiler():
            word = ""
            while True:
                char = file[self.index]

                if word == "" and char in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif word == "" and char == "\n": # newlines
                    increment_index()
                    line += 1

                elif char == '(' and peek() == '.': # comments
                    scan_comment()
                
                else:
                    if char in {" ", "\t", "\n"}:
                        self.compiler = word
                        increment_index()
                        return

                    word += char
                    increment_index()

        def scan_characters():
            key = ""
            word = ""
            while True:
                char = file[self.index]

                if peek_word() in SPECIFICATIONS:
                    break

                if char in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif char == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif char == '(' and peek() == '.': # comments
                    scan_comment()
                
                else:
                    if char == "=":
                        key = word
                        word = ""
                        increment_index()
                    elif char == '.':
                        word += char
                        self.characters[key] = word
                        key, word = "", "" # empty buffers
                        increment_index()

                    else:
                        word += char
                        increment_index()

        def scan_keywords():
            key = ""
            word = ""
            while True:
                char = file[self.index]

                if peek_word() in SPECIFICATIONS:
                    break

                if char in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif char == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif char == '(' and peek() == '.': # comments
                    scan_comment()
                
                else:
                    if char == "=":
                        key = word
                        word = ""
                        increment_index()
                    elif char == '.':
                        self.keywords[key] = word
                        key, word = "", "" # empty buffers
                        increment_index()

                    else:
                        word += char
                        increment_index()

        def scan_tokens():
            key = ""
            word = ""
            while True:
                char = file[self.index]

                if peek_word() in SPECIFICATIONS:
                    break

                if char in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif char == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif char == '(' and peek() == '.': # comments
                    scan_comment()
                
                else:
                    if char == "=":
                        key = word
                        word = ""
                        increment_index()
                    elif char == '.':
                        word += char
                        self.tokens[key] = word
                        key, word = "", "" # empty buffers
                        increment_index()

                    else:
                        word += char
                        increment_index()

        def preprocess_characters():
            """ Converts character set into a valid regular expression. """
            for character in self.characters:
                value = self.characters[character]

                queue = []
                word = ""
                i = 0
                scanning = True
                while scanning:
                    c = value[i]
                    
                    if c == '"':
                        i += 1
                        while value[i] != '"':
                            word += value[i]
                            i += 1
                    elif c in {"-", "+"}:
                        queue.append(word)
                        word = ""
                        queue.append(c)
                    elif c ==".":
                        queue.append(word)
                        break
                    else:
                        word += value[i]
                    
                    i += 1

                res = ""
                while len(queue) > 0:
                    value = queue.pop(0)
                    if value in self.characters:
                        res += self.characters[value]
                    elif value == "+":
                        res += queue.pop(0)
                    elif value == "-":
                        for c in queue.pop(0):
                            res = res.replace(c, "")
                    else:
                        res += value
                self.characters[character] = res
            
            for character in self.characters:
                res = ""
                for i, c in enumerate(self.characters[character]):
                    res += self.characters[character][i]
                    if i < (len(self.characters[character])-1):
                        res += '|'

                self.characters[character] = '(' + res + ')'
                print(character, self.characters[character])

        def preprocess_tokens():
            for token in self.tokens:
                value = self.tokens[token]
                print(token, value)

                res = ""
                word = ""
                i = 0
                scanning = True

                while scanning:
                    c = value[i]
                    
                    if c == '"':
                        i += 1
                        while value[i] != '"':
                            word += value[i]
                            i += 1
                    elif c in {"{", "}"}:
                        if word in self.characters:
                            res += self.characters[word]
                        else:
                            res += word
                        res += c
                        word = ""
                    elif c ==".":
                        res += word
                        break
                    else:
                        word += value[i]
                    
                    i += 1

                print(token, res)
                self.tokens[token] = res

        if expect("COMPILER"):
            scan_compiler()

        if expect("CHARACTERS"):
            scan_characters()
            preprocess_characters()
            print("\n")

        if expect("KEYWORDS"):
            scan_keywords()
        
        if expect("TOKENS"):
            scan_tokens()
            preprocess_tokens()

        if expect("PRODUCTIONS"):
            pass

        if expect("END"):
            pass
    
        return (
            self.characters,
            self.keywords,
            self.tokens,
            self.productions,
        )

                

if __name__ == "__main__":
    filename = "ejemploCocol.cocoL"
    scanner = Scanner(filename)

    scanner.scan()