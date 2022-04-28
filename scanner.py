from select import kevent
import string

LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)

SPECIFICATIONS = ["COMPILER", "CHARACTERS", "KEYWORDS", "TOKENS", "PRODUCTIONS", "END", "IGNORE"]

# ANY = [chr(i) for i in range(0, 65536)]

class Scanner:
    """ CoCoL parser. """

    compiler: str = ""
    characters: dict = {}
    keywords: dict = {}
    tokens: dict = {}
    productions: dict = {}
    except_keywords: dict = {}
    alphabet: set = set()
    ignore: set = set()

    index = 0
    line = 1

    def __init__(self, filename) -> None:
        self.filename = filename
        self.file = open(filename, "r").read()

    def increment_index(self, offset = 1):
        self.index += offset

    def peek(self, offset = 1) -> str:
        return self.file[self.index + offset]

    def peek_word(self,):
        word = ""
        temp_index = self.index
        while True:
            c = self.file[temp_index]

            if word != "" and c in {" ", "\t", "\n"}:
                break
            elif word == "" and c in {" ", "\t", "\n"}:
                temp_index += 1
            else:
                word += c
                temp_index += 1

        return word

    def peek_char(self,):
        char = ""
        temp_i = self.index
        while True:
            c = self.file[temp_i]

            if char == "" and c in {" ", "\t", "\n"}: # ignore whitespaces
                temp_i += 1
            else:
                return c

    def set_decl(self,):
        """ SetDecl = ident '=' Set. """

        ident = ""
        queue = []

        while True:
            c = self.file[self.index]
            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.line += 1
                self.increment_index()

            elif c == '=':
                self.increment_index() # '='
                queue = self._set()

            elif c in LETTER: # ident
                ident += c
                self.increment_index()
                c = self.file[self.index]
                while c in LETTER or c in DIGIT:
                    ident += c
                    self.increment_index()
                    c = self.file[self.index]

            elif c == '.':
                self.increment_index()

                char_set = self.preprocess_set(queue=queue)
                            
                self.characters[ident] = char_set
                return
  
    def _set(self,):
        """ Set = BasicSet { ('+'|'-') BasicSet }. """

        char_set = []

        basic_set = self.basic_set()

        while basic_set is not None:
            char_set.append(basic_set)
            basic_set = self.basic_set()

        return char_set

    def basic_set(self,):
        """ = string | ident | Char [".." Char]. """

        basic_set = set()
        while True:
            c = self.file[self.index]

            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.increment_index()
                self.line += 1
            
            elif c in {'+', '-'}:
                self.increment_index()
                return c

            # CHR(number)
            elif (self.index < (len(self.file) - 5)
                and self.file[self.index: self.index+4] == "CHR("):

                self.increment_index(4) # ignore CHR(
                char = 0
                while self.file[self.index] != ')':
                    char = char * 10 + int(self.file[self.index])
                    self.alphabet.add(char)
                    self.increment_index()
                
                self.increment_index() # ignore )
                return char

            elif (self.index < (len(self.file)-3)
                    and self.file[self.index: self.index+2] == ".."):
                self.increment_index(2)
                return ".."
            
            elif c == '\"': # string
                self.increment_index() # ignore "
                while self.file[self.index] != '\"':
                    c = ord(self.file[self.index])
                    basic_set.add(c)
                    self.alphabet.add(c)
                    self.increment_index()
                    
                self.increment_index() # ignore "
                return basic_set

            elif c == '\'': # char
                self.increment_index() # ignore '
                c = ord(self.file[self.index])
                self.alphabet.add(c)
                self.increment_index()
                self.increment_index() # ignore '

                return c
            
            elif c in LETTER: # ident
                ident = ""
                ident += c
                self.increment_index()
                c = self.file[self.index]
                while c in LETTER or c in DIGIT:
                    ident += c
                    self.increment_index()
                    c = self.file[self.index]
                
                if ident in self.characters:
                    return self.characters[ident]
            
            else:
                return None

    def preprocess_set(self, queue: list):
        char_set = set()
        # Create set
        while len(queue) > 0:
            value = queue.pop(0)

            if value == "+":
                value = queue.pop(0)
                if isinstance(value, int):
                    char_set.add(value)
                else:
                    char_set = char_set.union(value)
            elif value == "-":
                char_set = char_set.difference(queue.pop(0))
            elif len(queue) > 0 and queue[0] == "..":
                queue.pop(0) # pop ..
                upper_limit = queue.pop()
                for i in range(value, upper_limit+1):
                    self.alphabet.add(i)
                range_set = {i for i in range(value, upper_limit + 1)}
                char_set = char_set.union(range_set)

            else:
                if isinstance(value, int):
                    char_set.add(value)
                else:
                    char_set = char_set.union(set(value))
                    
        
        return char_set

    def keyword_decl(self,):
        """ KeywordDecl = ident '=' string '.'. """

        ident = ""
        string = []

        while True:
            c = self.file[self.index]
            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.line += 1
                self.increment_index()

            elif c == '=':
                self.increment_index() # '='
                # string = self.token_expr()

            elif c in LETTER: # ident
                ident += c
                self.increment_index()
                c = self.file[self.index]
                while c in LETTER or c in DIGIT:
                    ident += c
                    self.increment_index()
                    c = self.file[self.index]

            elif c == '\"': # string
                self.increment_index() #ignore "
                while self.file[self.index] != '\"':
                    c = ord(self.file[self.index])
                    string.append(c)
                    self.alphabet.add(c)
                    self.increment_index()
                
                self.increment_index() # ignore " 


            elif c == '.':
                self.keywords[ident] = string
                self.increment_index()

                return

    def token_decl(self,):
        """ TokenDecl = ident ['=' TokenExpr ] ["EXCEPT KEYWORDS"] '.'. """

        ident = ""
        expr = ""

        while True:
            c = self.file[self.index]
            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.line += 1
                self.increment_index()

            elif c == '=':
                self.increment_index() # '='
                expr = self.token_expr()

            elif c in LETTER: # ident
                ident += c
                self.increment_index()
                c = self.file[self.index]
                while c in LETTER or c in DIGIT:
                    ident += c
                    self.increment_index()
                    c = self.file[self.index]

            elif c == '.':
                check_kwrds = ''.join(chr(c) if isinstance(c, int) else c for c in expr[-14:])
                if check_kwrds == "EXCEPTKEYWORDS":
                    self.except_keywords[ident] = True
                    expr = expr[:-14] # remove "EXCEPT KEYWORDS"

                # print(ident)
                # print(''.join(str(c) + " " for c in expr))
                self.tokens[ident] = expr
                self.increment_index()

                return
          
    def token_expr(self,):
        """ TokenExpr = TokenTerm {'|' TokenTerm }. """

        expr = []

        expr += self.token_term()

        while self.peek_char() == '|':
            expr += '|'
            self.increment_index()
            expr += self.token_term()

        return expr

    def token_term(self,):
        """ TokenTerm = TokenFactor {TokenFactor} """

        term = []

        factor = self.token_factor()
        while factor is not None:
            term += factor
            factor = self.token_factor()

        return term

    def token_factor(self,):
        """ TokenFactor = Symbol
                        | '(' TokenExpr ')'
                        | '[' TokenExpr ']'
                        | '{' TokenExpr '}'.
        """

        factor = []

        while True:
            c = self.file[self.index]
            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.increment_index()
                self.line += 1

            elif c == '(':
                self.increment_index() # (
                self.factor += '('
                factor += self.token_expr()
                self.factor += ')'
                self.increment_index() # )

                return factor
            
            elif c == '[':
                self.increment_index() # [
                factor += '('
                factor += self.token_expr()
                factor += ')?'
                self.increment_index() # ]
                
                return factor

            elif c == '{':
                self.increment_index() # {
                factor += '('
                factor += self.token_expr()
                factor += ')*'
                self.increment_index() # }
            
                return factor

            else:
                s = self.symbol()
                if s is not None:
                    factor += s
                    return factor
                else:
                    return None

    def symbol(self,):
        """ Symbol = ident | string | char """
        
        symbol = []
        while True:
            c = self.file[self.index]

            if c in {" ", "\t"}: # whitespaces and tabs
                self.increment_index()

            elif c == "\n": # newlines
                self.increment_index()
                self.line += 1
            
            elif c == '\"': # string
                self.increment_index() # '"'
                symbol += '('
                while self.file[self.index] != '\"':
                    c = ord(self.file[self.index])
                    symbol.append(c)
                    self.alphabet.add(c)
                    self.increment_index()
                    
                self.increment_index() # '"'
                symbol += ')'

                return symbol

            elif c == '\'': # char
                self.increment_index()
                symbol += '('
                symbol = ord(self.file[self.index])
                self.alphabet.add(ord(self.file[self.index]))
                symbol += ')'
                self.increment_index()

                return symbol
            
            elif c in LETTER: # ident
                ident = ""
                ident += c
                self.increment_index()
                c = self.file[self.index]
                while c in LETTER or c in DIGIT:
                    ident += c
                    self.increment_index()
                    c = self.file[self.index]
                
                if ident in self.characters:
                    symbol += '('
                    for i, char in enumerate(self.characters[ident]):
                        if i == (len(self.characters[ident])-1):
                            symbol.append(char)
                        else:
                            symbol.append(char)
                            symbol.append('|')

                    symbol += ')'

                else:
                    symbol += ident

                return symbol
            
            else:
                return None

    def scan(self, filename = None):
        """ Parse COCOl filename. """
        
        self.index = 0
        self.line = 1


        def scan_comment():
            self.increment_index(2)
            comment = ""
            while self.file[self.index] != "." and self.peek() != ')':
                comment += self.file[self.index]
                self.increment_index()
            self.increment_index(2)
        
        def expect(word) -> bool:
            """ Read expected word from self.file. """

            word_pos = 0
            matches = True
            temp_i = self.index

            while True:
                c = self.file[temp_i]

                if c in {" ", "\t"}: # whitespaces and tabs
                    self.increment_index()
                    temp_i += 1

                elif c == "\n": # newlines
                    self.increment_index()
                    temp_i += 1
                    self.line += 1

                elif c == '(' and self.peek() == '.': # comments
                    scan_comment()
                    temp_i = self.index
                
                elif c == word[word_pos]:
                        temp_i += 1
                        word_pos += 1
                        matches = True
                else:
                    return False
                
                if word_pos == len(word):
                    if matches:
                        self.index = temp_i
                    return matches

        def scan_compiler():
            compiler = ""
            while True:
                c = self.file[self.index]

                if c in {" ", "\t"}: # whitespaces and tabs
                    self.increment_index()

                elif c == "\n": # newlines
                    self.increment_index()
                    self.line += 1

                elif c == '(' and self.peek() == '.': # comments
                    scan_comment()

                elif c in LETTER: # ident
                    compiler += c
                    self.increment_index()
                    c = self.file[self.index]
                    while c in LETTER or c in DIGIT:
                        compiler += c
                        self.increment_index()
                        c = self.file[self.index]

                    return compiler


        if expect("COMPILER"):
            self.compiler = scan_compiler()
            print("Compiler: ", self.compiler)

        if expect("CHARACTERS"):
            print("Starting characters scanning.")
            # scan_characters()
            while self.peek_word() not in SPECIFICATIONS:
                self.set_decl()
            
            print("Done scanning characters!")

        if expect("KEYWORDS"):
            print("Starting keywords scanning.")
            while self.peek_word() not in SPECIFICATIONS:
                self.keyword_decl()
            
            print("Done scanning keywords!")
        
        if expect("TOKENS"):
            print("Starting tokens scanning.")
            while self.peek_word() not in SPECIFICATIONS:
                self.token_decl()

            # add keywords
            for kw in self.keywords:
                self.tokens[kw] = self.keywords[kw]

            print("Done scanning tokens!")
        
        if expect("IGNORE"):
            queue = self._set()
            self.ignore = self.preprocess_set(queue=queue)

            print("Done scanning ignore!")

        if expect("PRODUCTIONS"):
            pass

        if expect("END"):
            if scan_compiler() == self.compiler and self.peek_char() == '.':
                print("CoCoL scanning end!")
    
        return (
            self.compiler,
            self.characters,
            self.keywords,
            self.tokens,
            self.productions,
            self.except_keywords,
            self.ignore,
            self.alphabet
        )
         

if __name__ == "__main__":
    filename = "tests/ejemploCocol.cocoL"
    scanner = Scanner(filename)

    scanner.scan()

    print(scanner.tokens)
