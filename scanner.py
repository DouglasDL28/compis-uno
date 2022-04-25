import re


SPECIFICATIONS = ["COMPILER", "CHARACTERS", "KEYWORDS", "TOKENS", "PRODUCTIONS", "END"]

class Scanner:
    """ CoCoL parser. """

    compiler: str = ""
    characters: dict = {}
    keywords: set = set()
    tokens: dict = {}
    productions: dict = {}
    except_keywords: dict = {}

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

                    elif char == "\"":
                        increment_index() #ignore "
                        while file[self.index] != "\"":
                            word += file[self.index]
                            increment_index()
                        
                        increment_index() # ignore " 
                    elif char == '.':
                        self.keywords.add(word)
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
                    
                    if c == '\"':
                        i += 1
                        while value[i] != '\"':
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

        def preprocess_tokens():
            for name in self.tokens:
                token = self.tokens[name]

                res = ""
                word = ""
                i = 0
                scanning = True

                if token[-15: -1] == "EXCEPTKEYWORDS":
                    token = token[0:-15] + '.'
                    self.except_keywords[name] = True

                print(token)

                while scanning:
                    c = token[i]
                    
                    if c == '\"':
                        i += 1
                        while token[i] != '\"':
                            word += token[i]
                            i += 1
                    
                    elif c == '{':
                        i += 1
                        # add word previous to brakers
                        if word in self.characters:
                            res += self.characters[word]
                        else:
                            res += word

                        res += '(' # open Kleene
                        word = "" # reset buffer

                        # scan word inside brackets
                        while token[i] != '}':
                            word += token[i]
                            i += 1
                        
                        # add word inside brackets
                        if word in self.characters:
                            res += self.characters[word]
                        else:
                            res += word
                        
                        res += ")*" # close Kleene
                        word = "" # reset buffer

                    elif c == '[':
                        i += 1
                        # add word previous to brakers
                        if word in self.characters:
                            res += self.characters[word]
                        else:
                            res += word

                        res += '(' # open Kleene
                        word = "" # reset buffer

                        # scan word inside brackets
                        while token[i] != ']':
                            word += token[i]
                            i += 1
                        
                        # add word inside brackets
                        if word in self.characters:
                            res += self.characters[word]
                        else:
                            res += word
                        
                        res += ")?" # close Kleene
                        word = "" # reset buffer

                    elif c ==".":
                        res += word
                        scanning = False
                    else:
                        word += token[i]
                    
                    i += 1

                self.tokens[name] = res

        if expect("COMPILER"):
            scan_compiler()

        if expect("CHARACTERS"):
            scan_characters()
            preprocess_characters()

        if expect("KEYWORDS"):
            scan_keywords()
        
        if expect("TOKENS"):
            scan_tokens()
            preprocess_tokens()

            # add keywords
            for kw in self.keywords:
                self.tokens[kw] = kw

            print(self.tokens)

        if expect("PRODUCTIONS"):
            pass

        if expect("END"):
            pass
    
        return (
            self.characters,
            self.keywords,
            self.tokens,
            self.productions,
            self.except_keywords
        )
         

if __name__ == "__main__":
    filename = "ejemploCocol.cocoL"
    scanner = Scanner(filename)

    scanner.scan()

    print(scanner.tokens)