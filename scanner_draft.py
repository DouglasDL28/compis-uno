

SPECIFICATIONS = ["COMPILER", "CHARACTERS", "KEYWORDS", "TOKENS", "PRODUCTIONS", "END"]

ANY = [chr(i) for i in range(0, 65536)]

print(len(ANY))

class Scanner:
    """ CoCoL parser. """

    compiler: str = ""
    characters: dict = {}
    keywords: dict = {}
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

            queue = [] # tokens queue

            while True:
                c = file[self.index]

                if peek_word() in SPECIFICATIONS:
                    break

                # CHR(number)
                if (self.index < (len(file) - 5)
                    and file[self.index: self.index+4] == "CHR"):

                    increment_index(4)
                    char = 0
                    while file[self.index] != ')':
                        char = char * 10 + file[self.index]
                        increment_index()
                    
                    queue.append(chr(char))
                    increment_index()
                
                elif (self.index < (len(file)-3)
                      and file[self.index: self.index+2] == ".."):
                    queue.append("..")
                    increment_index(2)

                elif c in {'+', '-'}:
                    # push ident if available
                    if word:
                        queue.append(word)
                    queue.append(c)
                    increment_index()
                
                elif c == "\"": # string
                    increment_index()
                    string = ""
                    while file[self.index] != "\"":
                        string += file[self.index]
                        increment_index()
                    increment_index()
                    queue.append(string)
                
                elif c == "\'": # char
                    increment_index()
                    queue.append(file[self.index])
                    increment_index()

                elif c in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif c == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif c == '(' and peek() == '.': # comments
                    scan_comment()

                elif c == '=':
                    key = word
                    self.characters[key] = set()
                    word = "" # empty buffer
                    increment_index()

                elif c == '.': # end SetDecl
                    if word:
                        queue.append(word)
                    increment_index()

                    # Create set
                    while len(queue) > 0:
                        value = queue.pop(0)
                        print(self.characters)
                        if value in self.characters:
                            self.characters[key] = self.characters[key].union(self.characters[value])
                        elif value == "+":
                            self.characters[key] = self.characters[key].union(queue.pop(0))
                        elif value == "-":
                            self.characters[key] = self.characters[key].difference(queue.pop(0))
                        elif len(queue) > 1 and queue[0] == "..":
                            queue.pop(0) # pop ..
                            self.characters[key] = self.characters[key].union({
                                i for i in range(value, queue.pop() + 1)
                            })
                            print(value, "..", queue.pop(0))

                        else:
                            self.characters[key] = self.characters[key].union(set(value))

                    key, word = "", "" # empty buffers

                else:
                    word += c
                    increment_index()

            print("queue\n", queue)

        def scan_keywords():
            """ Scan Keywords Declarations. """

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
                    elif char == '.': # end KeywordDecl
                        self.keywords[key] = word
                        key, word = "", "" # empty buffers
                        increment_index()

                    else:
                        word += char
                        increment_index()

        def scan_tokens():
            key = ""
            word = ""
            token = ""

            while True:
                c = file[self.index]

                if peek_word() in SPECIFICATIONS:
                    break

                # except keywords
                if (self.index < (len(file) - 17)
                    and file[self.index: self.index + 16] == "EXCEPT KEYWORDS"):

                    self.except_keywords[key] = True
                    increment_index(16)

                elif c in {" ", "\t"}: # whitespaces and tabs
                    increment_index()

                elif c == "\n": # newlines
                    increment_index()
                    self.line += 1

                elif c == '(' and peek() == '.': # comments
                    scan_comment()
                
                elif c == '=':
                    key = word
                    word = "" # empty buffer
                    increment_index()
                
                elif c == '\"': # string
                    increment_index()
                    string = "("
                    while file[self.index] != '\"':
                        string += file[self.index]
                        increment_index()
                    increment_index()
                    string += ')'

                    token += string
                    # queue.append(string)
                
                elif c == "\'": # char
                    increment_index()
                    token += '(' + file[self.index] + ')'
                    increment_index()

                elif c == '{':
                    temp = ""
                    increment_index()
                    # add word previous to brackets
                    if word in self.characters: # ident
                        token += self.characters[word]

                    token += '(' # open Kleene
                    word = "" # reset buffer

                    # scan word inside brackets
                    while file[self.index] != '}':
                        word += file[self.index]
                        increment_index()
                    
                    # add word inside brackets
                    if word in self.characters: # ident
                        token += self.characters[word]
                    
                    token += ")*" # close Kleene
                    word = "" # reset buffer

                    

                elif c == '{':
                    pass
                
                elif c == '[':
                    pass

                # TODO end TokenDecl
                elif c == '.':
                    self.tokens[key] = token
                    key, word = "", "" # empty buffers
                    increment_index()

                else: # ident
                    word += c
                    increment_index

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

                if token[-16: -1] == "EXCEPT KEYWORDS":
                    token = token[0:-16] + '.'
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
            # preprocess_characters()

        if expect("KEYWORDS"):
            scan_keywords()
        
        if expect("TOKENS"):
            scan_tokens()
            preprocess_tokens()

            # add keywords
            for kw in self.keywords:
                self.tokens[kw] = kw

        if expect("PRODUCTIONS"):
            pass

        if expect("END"):
            # scan_compiler()
            pass
    
        return (
            self.compiler,
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
