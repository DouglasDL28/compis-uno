import os
import string

from scan import Scanner, Token
from RegularExpression import RegularExpression as RE
from proyecto2 import generate_file
from node.parse_node import (
    ParseNode, ParseKleeneNode, ParseConcatNode,
    ParseOrNode, ParseOptionalNode, ParseSymbolNode,
    ParseSemActionNode, ParseAttributesNode
)

LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)

SPECIFICATIONS = ["COMPILER", "CHARACTERS", "KEYWORDS", "TOKENS", "PRODUCTIONS", "END", "IGNORE"]


class CompilerGenerator:
    """ Lexer and parser generator. """

    compiler: str = ""
    characters: dict = {}
    keywords: dict = {}
    tokens: dict = {}
    token_names: list = []
    productions: dict[str, ParseNode] = {}
    signatures: dict[str, str] = {}
    rvs: dict[str, str] = {}
    except_keywords: dict = {}
    alphabet: set = set()
    ignore: set = set()

    index = 0
    line = 1

    def __init__(self, token_stream) -> None:
        self.token_stream: list[Token] = token_stream # queue

    def peek(self):
        return self.token_stream[0]
    
    def get(self):
        return self.token_stream.pop(0)

    def scanner_spec(self,):
        """ ScannerSpecification =
                    ["CHARACTERS" {SetDecl}]
                    ["KEYWORDS" {KeywordDecl}]
                    ["TOKENS" {TokenDecl}]
                    {WhiteSpaceDecl}.
        """

        if self.peek().lexeme == "CHARACTERS":
            self.get() # pop "CHARACTERS"
            while self.peek().lexeme not in SPECIFICATIONS:
                self.set_decl()
        if self.peek().lexeme == "KEYWORDS":
            self.get() # pop "KEYWORDS"
            while self.peek().lexeme not in SPECIFICATIONS:
                self.keyword_decl()
        
        if self.peek().lexeme == "TOKENS":
            self.get() # pop "TOKENS"
            while self.peek().lexeme not in SPECIFICATIONS:
                self.token_decl()
        
        while self.peek().lexeme == "IGNORE":
            self.get() # pop "IGNORE"
            queue = self._set()
            self.ignore = self.ignore.union(self.preprocess_set(queue=queue))
              
    def parser_spec(self,):
        """ ParserSpecification = "PRODUCTIONS" {Production}. """

        self.get() # pop "PRODUCTIONS"

        while self.peek().lexeme != "END":
            self.production()

    def production(self,):
        """ Production = ident [Attributes] [SemAction] '=' Expression '.'. """

        ident = ""
        attr = None
        expression = None

        while True:
            token = self.get()

            if token.name == "ident":
                ident = token.lexeme
            if token.lexeme == "<": # attribute
                attr = self.attributes()
            if token.name == "startSemAction":
                self.sem_action()
            if token.lexeme == "=":
                expression = self.expression()
            if token.lexeme == ".":
                if attr:
                    self.signatures[ident] = f"{ident}(self, {attr.value})"
                    self.rvs[ident] = f"return {attr.rv}" if attr.rv else ""
                else:
                    self.signatures[ident] = f"{ident}(self)"
                
                self.productions[ident] = expression

                return

    def expression(self,):
        """ Expression = Term{'|'Term}. """

        expr = self.term()

        while self.peek().lexeme == '|':
            self.get() # |
            
            temp = ParseOrNode("|")
            temp.left = expr
            temp.right = self.term()

            expr = temp


        return expr

    def term(self,):
        """ Term = Factor {Factor} """

        factor = self.factor()
        term = factor
        
        while factor is not None:
            factor = self.factor()
            if factor is not None:
                temp = ParseConcatNode("•")
                temp.left = term
                temp.right = factor
                term = temp

        return term

    def factor(self,):
        """ Factor = Symbol [Attributes]
                    | '(' Expression ')'
                    | '[' Expression ']'
                    | '{' Expression '}'
                    | SemAction.
        """

        factor = None

        token = self.peek()

        if token.lexeme == '(':
            self.get() # (
            factor = ParseConcatNode("•")
            factor.left = self.expression()
            self.get() # )
        
        elif token.lexeme == '[':
            self.get() # [
            factor = ParseOptionalNode("?")
            factor.left = self.expression()
            self.get() # ]

        elif token.lexeme == '{':
            self.get() # {
            factor = ParseKleeneNode("*")
            factor.left = self.expression()
            self.get() # }

        elif token.name == "startSemAction":
            self.get()
            factor = self.sem_action()

        elif token.name == "string": # symbol
            self.get()
            lexeme = token.lexeme[1:-1]
            factor = ParseSymbolNode(lexeme)
            if lexeme not in self.tokens:
                self.token_names.insert(0, lexeme) # insert to front
                self.tokens[lexeme] = ['('] + [ord(i) for i in lexeme] + [')']
                self.alphabet = self.alphabet.union({ord(c) for c in lexeme})
            if self.peek().lexeme == "<":
                self.get() # <
                factor.left = self.attributes()

        elif token.name == "char": # symbol
            self.get()
            factor = ParseSymbolNode(token.lexeme)
            if self.peek().lexeme == "<":
                self.get() # <
                factor.left = self.attributes()

        elif token.name == "ident": # symbol
            self.get()
            factor = ParseSymbolNode(token.lexeme)
            if self.peek().lexeme == "<":
                self.get() # <
                factor.left = self.attributes()
        
        else:
            return None

        return factor

    def attributes(self,):
        """ Attributes = "<" {ANY} ">" """   
        
        attr = ""
        rv = None

        while self.peek().lexeme != ">":
            token = self.get()

            if token.lexeme == '$':
                rv = self.get().lexeme
            else:
                attr += token.lexeme
        self.get() # >

        return ParseAttributesNode(attr, rv=rv)

    def sem_action(self,):
        """ SemAction = "(." {ANY} ".)" """

        action = ""

        while self.peek().name != "endSemAction":
            token = self.get()
            action += token.lexeme
        self.get() # endSemAction

        return ParseSemActionNode(action)        

    def set_decl(self,):
        """ SetDecl = ident '=' Set. """

        ident = ""
        queue = []

        while True:
            token = self.get()
            if token.name == "ident":
                ident = token.lexeme

            elif token.lexeme == '=':
                queue = self._set()

            elif token.lexeme == '.':
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
            token = self.peek()

            if token.lexeme in {'+', '-'}:
                self.get()
                return token.lexeme

            # CHR(number)
            elif token.name == "charnumber":
                self.get()
                char = int(token.lexeme[4:-1])
                self.alphabet.add(char)
                return char

            elif token.lexeme == "..":
                self.get()
                return token.lexeme
            
            elif token.name == "string":
                self.get()

                string_set = { ord(c) for c in token.lexeme[1:-1] }
                basic_set = basic_set.union(string_set)
                self.alphabet = self.alphabet.union(string_set)

                return basic_set

            elif token.name == "char":
                self.get()
                c = ord(token.lexeme)
                self.alphabet.add(c)
                return c
            
            elif token.name == "ident":
                self.get()
                if token.lexeme in self.characters:
                    return self.characters[token.lexeme]
            
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
            token = self.get()

            if token.lexeme == '=':
                token = self.get()

                if token.name == "string": # string
                    string = [ord(c) for c in token.lexeme[1:-1]]
                    self.alphabet = self.alphabet.union(set(string))

            elif token.name == "ident": # ident
                ident = token.lexeme

            elif token.lexeme == '.':
                self.keywords[ident] = string

                return

    def token_decl(self,):
        """ TokenDecl = ident ['=' TokenExpr ] ["EXCEPT KEYWORDS"] '.'. """

        ident = ""
        expr = ""

        while True:
            token = self.get()

            if token.lexeme == '=':
                expr = self.token_expr()

            elif token.name == "ident": # ident
                ident = token.lexeme

            elif token.lexeme == '.':
                check_kwrds = "".join(chr(c) if isinstance(c, int) else c for c in expr[-14:])
                if check_kwrds == "EXCEPTKEYWORDS":
                    expr = expr[:-14]
                    self.except_keywords[ident] = True

                self.tokens[ident] = expr
                self.token_names.append(ident)

                return
          
    def token_expr(self,):
        """ TokenExpr = TokenTerm {'|' TokenTerm }. """

        expr = []

        expr += self.token_term()

        while self.peek().lexeme == '|':
            self.get()
            expr += '|'
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

        token = self.peek()

        if token.lexeme == '(':
            self.get()
            factor += '('
            factor += self.token_expr()
            factor += ')'
            self.get() # )
        
        elif token.lexeme == '[':
            self.get()
            factor += '('
            factor += self.token_expr()
            factor += ')?'
            self.get() # ]

        elif token.lexeme == '{':
            self.get()
            factor += '('
            factor += self.token_expr()
            factor += ')*'
            self.get() # }

        elif token.name == "string": # string
            self.get()
            factor += '('
            string_arr = [ ord(c) for c in token.lexeme[1:-1] ]
            factor += string_arr
            self.alphabet = self.alphabet.union(set(string_arr))
            factor += ')'

        elif token.name == "char":
            self.get()
            factor += '('
            char = ord(token.lexeme)
            factor.append(char)
            self.alphabet.add(char)
            factor += ')'

        elif token.name == "ident":
            self.get()
            ident = token.lexeme
            if token.lexeme in self.characters:
                factor += '('

                for i, char in enumerate(self.characters[ident]):
                    if i == (len(self.characters[ident])-1):
                        factor.append(char)
                    else:
                        factor.append(char)
                        factor.append('|')
                factor += ')'
            
            else:
                print(f"ident '{ident}' no identificado!")
                factor = ident

        else:
            return None

        return factor

    def scan(self, filename = None):
        """ Parse COCOl filename. """
        
        self.index = 0
        self.line = 1

        token = self.get()
        if token.lexeme == "COMPILER":
            self.compiler = self.get()
            print("Compiler: ", self.compiler)

            self.scanner_spec()
            self.parser_spec()

            token = self.get()
            if token.lexeme == "END":
                token = self.get()
                if token.lexeme == self.compiler:
                    return
    
        return (
            self.compiler,
            self.characters,
            self.keywords,
            self.tokens,
            self.token_names,
            self.productions,
            self.signatures,
            self.rvs,
            self.except_keywords,
            self.ignore,
            self.alphabet
        )
         

if __name__ == "__main__":

    scanner = Scanner()

    # filename = input("Input filename: ") or "tests/1.atg"
    filename = input("Input atg file: ") or "tests/3.atg"
    print("Generating compiler for " + filename + "...")

    sim, tokens, elapsed_t  = scanner.simulate(filename=filename)

    generator = CompilerGenerator(token_stream=tokens) # process tokens
    compiler, characters, keywords, tokens, token_names, productions, \
    signatures, rvs, except_keywords, ignore, alphabet = generator.scan()

    re = []
    for i, name in enumerate(token_names):
        re += '('
        re += tokens[name] 
        re += ")#"
        if i < (len(tokens) - 1):
            re += "|"


    re = RE(re, alphabet=alphabet, ignore=ignore)
    dfa, elapsed_t = re.direct_construction(token_names, keywords, except_keywords)
    print("Direct Construction elapsed time: ", elapsed_t)

    if not os.path.isdir(f"{compiler.lexeme}"):
        os.mkdir(f"{compiler.lexeme}")

    generate_file(filename=f"{compiler.lexeme}/lexer.py", template_file="scanner.txt", data={
        "F": dfa.F,
        "delta": dfa.delta,
        "Q": dfa.Q,
        "Sigma": dfa.Sigma,
        "q_init": dfa.q_init,
        "token_names": dfa.token_names,
        "token_states": dfa.token_states,
        "keywords": dfa.keywords,
        "except_keyword": dfa.except_keyword,
        "ignore": ignore
    })

    print("Scanner generated successfully!")

    firstpos: dict[str, set] = {}

    ParseNode.productions = productions
    for prod in productions:
        firstpos[prod] = productions[prod].firstpos()
    ParseNode.first = firstpos

    parser_file = open(f"{compiler.lexeme}/parser.py", 'w')
    ParseNode.parser_file = parser_file

    parser_file.write("""
from scan import Token 

class Parser():
    token_stream: list[Token] = []
    la: Token = None    # look ahead token
    t: Token = None     # token

    def syn_error(self, expected):
        print(f"Syntax error. Expected {expected}.")

    def expect(self, token):
        if token == self.la.name:
            self.get()
        else:
            self.syn_error(token)

    def get(self):
        self.t = self.la
        if self.token_stream: # check if empty
            self.la = self.token_stream.pop(0)

    def parse(self, token_stream):
        self.token_stream = token_stream
        self.get()
""")

    parser_file.write(" "*8 + "self." + next(iter(productions)) + "()\n\n")

    for prod in productions:
        parser_file.write(" "*4 + "def " + signatures[prod] + ':\n')
        tree = productions[prod]
        tree.gen_code(tree, lvl=2)
        if prod in rvs:
            parser_file.write(" "*4*2 + rvs[prod] + '\n')
        parser_file.write("\n")

    parser_file.close()

    generate_file(filename=f"{compiler.lexeme}/compiler.py", template_file="compiler.txt", data={})

    



