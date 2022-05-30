
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
        self.MyCOCOR()

    def MyCOCOR(self):
        CompilerName="";EndName="";
        self.expect("COMPILER")
        CompilerName = self.Ident(CompilerName)
        print(f"NombreInicialdelCompilador:{CompilerName}");
        if self.la.name in {"startcode"}:
            self.Codigo()
        self.Body()
        self.expect("END")
        EndName = self.Ident(EndName)
        print(f"NombreFinaldelCompilador:{EndName}");

    def Body(self):
        self.Characters()
        if self.la.name in {"KEYWORDS"}:
            self.Keywords()
        self.Tokens()
        while self.la.name in {"IGNORE"}:
            self.WhitespaceDecl()
        self.Productions()

    def WhitespaceDecl(self):
        self.expect("IGNORE")
        self.CharSet()
        while self.la.name in {"+","-"}:
            if self.la.name in {"+"}:
                self.expect("+")
                self.CharSet()
            elif self.la.name in {"-"}:
                self.expect("-")
                self.CharSet()
            else: self.syn_error({'+', '-'})
        self.expect(".")

    def Characters(self):
        CharName="";Counter=0;
        self.expect("CHARACTERS")
        print("LEYENDOCHARACTERS");
        while self.la.name in {"ident"}:
            CharName = self.Ident(CharName)
            Counter+=1;print(f"CharSet{Counter}:{CharName}");
            self.expect("=")
            self.CharSet()
            while self.la.name in {"+","-"}:
                if self.la.name in {"+"}:
                    self.expect("+")
                    self.CharSet()
                elif self.la.name in {"-"}:
                    self.expect("-")
                    self.CharSet()
                else: self.syn_error({'+', '-'})
            self.expect(".")

    def Keywords(self):
        KeyName="";StringValue="";Counter=0;
        self.expect("KEYWORDS")
        print("LEYENDOKEYWORDS");
        while self.la.name in {"ident"}:
            KeyName = self.Ident(KeyName)
            Counter+=1;print(f"KeyWord{Counter}:{KeyName}");
            self.expect("=")
            StringValue = self.String(StringValue)
            self.expect(".")

    def Tokens(self):
        TokenName="";Counter=0;
        self.expect("TOKENS")
        print("LEYENDOTOKENS");
        while self.la.name in {"ident"}:
            TokenName = self.Ident(TokenName)
            Counter+=1;print(f"Token{Counter}:{TokenName}");
            self.expect("=")
            self.TokenExpr()
            if self.la.name in {"EXCEPT"}:
                self.ExceptKeyword()
            self.expect(".")

    def Productions(self):
        Counter=0;
        self.expect("PRODUCTIONS")
        ProdName="";print("LEYENDOPRODUCTIONS");
        while self.la.name in {"ident"}:
            ProdName = self.Ident(ProdName)
            Counter+=1;print(f"Production{Counter}:{ProdName}");
            if self.la.name in {"<"}:
                self.Atributos()
            self.expect("=")
            if self.la.name in {"startcode"}:
                self.Codigo()
            self.ProductionExpr()
            self.expect(".")

    def ExceptKeyword(self):
        self.expect("EXCEPT")
        self.expect("KEYWORDS")

    def ProductionExpr(self):
        self.ProdTerm()
        while self.la.name in {"|"}:
            self.expect("|")
            self.ProdTerm()

    def ProdTerm(self):
        self.ProdFactor()
        while self.la.name in {"[","char","{","string","(","ident"}:
            self.ProdFactor()

    def ProdFactor(self):
        if self.la.name in {"[","char","string","(","ident"}:
            if self.la.name in {"ident","(","string","char"}:
                if self.la.name in {"ident","string","char"}:
                    self.SymbolProd()
                elif self.la.name in {"("}:
                    self.expect("(")
                    self.ProductionExpr()
                    self.expect(")")
                else: self.syn_error({'ident', '(', 'string', 'char'})
            elif self.la.name in {"["}:
                self.expect("[")
                self.ProductionExpr()
                self.expect("]")
            else: self.syn_error({'[', 'char', 'string', '(', 'ident'})
        elif self.la.name in {"{"}:
            self.expect("{")
            self.ProductionExpr()
            self.expect("}")
        else: self.syn_error({'[', 'char', '{', 'string', '(', 'ident'})
        if self.la.name in {"startcode"}:
            self.Codigo()

    def SymbolProd(self):
        SV="";IN="";
        if self.la.name in {"string","char"}:
            if self.la.name in {"string"}:
                SV = self.String(SV)
                print(f"StringenProduction:{SV}");
            elif self.la.name in {"char"}:
                self.expect("char")
            else: self.syn_error({'string', 'char'})
        elif self.la.name in {"ident"}:
            IN = self.Ident(IN)
            print(f"IdentificadorenProduction:{IN}");
            if self.la.name in {"<"}:
                self.Atributos()
        else: self.syn_error({'ident', 'string', 'char'})

    def Codigo(self):
        self.expect("startcode")
        while self.la.name in {"TOKENS","char","{","=","+","-","KEYWORDS","}","CHARACTERS",".","charnumber","string",";",")","charinterval","ident","PRODUCTIONS","nontoken","("}:
            self.ANY()
        self.expect("endcode")

    def Atributos(self):
        self.expect("<")
        while self.la.name in {"TOKENS","char","{","=","+","-","KEYWORDS","}","CHARACTERS",".","charnumber","string",";",")","charinterval","ident","PRODUCTIONS","nontoken","("}:
            self.ANY()
        self.expect(">")

    def TokenExpr(self):
        self.TokenTerm()
        while self.la.name in {"|"}:
            self.expect("|")
            self.TokenTerm()

    def TokenTerm(self):
        self.TokenFactor()
        while self.la.name in {"[","char","{","string","(","ident"}:
            self.TokenFactor()

    def TokenFactor(self):
        if self.la.name in {"[","char","string","(","ident"}:
            if self.la.name in {"ident","(","string","char"}:
                if self.la.name in {"ident","string","char"}:
                    self.SimbolToken()
                elif self.la.name in {"("}:
                    self.expect("(")
                    self.TokenExpr()
                    self.expect(")")
                else: self.syn_error({'ident', '(', 'string', 'char'})
            elif self.la.name in {"["}:
                self.expect("[")
                self.TokenExpr()
                self.expect("]")
            else: self.syn_error({'[', 'char', 'string', '(', 'ident'})
        elif self.la.name in {"{"}:
            self.expect("{")
            self.TokenExpr()
            self.expect("}")
        else: self.syn_error({'[', 'char', '{', 'string', '(', 'ident'})

    def SimbolToken(self):
        IdentName="";StringValue="";
        if self.la.name in {"string","char"}:
            if self.la.name in {"string"}:
                StringValue = self.String(StringValue)
            elif self.la.name in {"char"}:
                self.expect("char")
            else: self.syn_error({'string', 'char'})
        elif self.la.name in {"ident"}:
            IdentName = self.Ident(IdentName)
            print(f"IdentificadorenToken:{IdentName}");
        else: self.syn_error({'ident', 'string', 'char'})

    def CharSet(self):
        IdentName="";StringValue="";
        if self.la.name in {"charnumber","string","charinterval","char"}:
            if self.la.name in {"string"}:
                StringValue = self.String(StringValue)
            elif self.la.name in {"charnumber","charinterval","char"}:
                self.Char()
            else: self.syn_error({'charnumber', 'string', 'charinterval', 'char'})
        elif self.la.name in {"ident"}:
            IdentName = self.Ident(IdentName)
            print(f"IdentificadorenCharSet:{IdentName}");
        else: self.syn_error({'char', 'charnumber', 'string', 'charinterval', 'ident'})

    def Char(self):
        if self.la.name in {"charnumber","char"}:
            if self.la.name in {"char"}:
                self.expect("char")
            elif self.la.name in {"charnumber"}:
                self.expect("charnumber")
            else: self.syn_error({'charnumber', 'char'})
        elif self.la.name in {"charinterval"}:
            self.expect("charinterval")
        else: self.syn_error({'charnumber', 'charinterval', 'char'})

    def String(self, S):
        self.expect("string")
        S=self.t.lexeme;
        return S

    def Ident(self, S):
        self.expect("ident")
        S=self.t.lexeme;
        return S

    def ANY(self):
        if self.la.name in {"TOKENS","char","{","=","+","-","KEYWORDS","}","CHARACTERS",".","charnumber","string",";",")","charinterval","ident","nontoken","("}:
            if self.la.name in {"TOKENS","char","{","=","+","-","}","CHARACTERS",".","charnumber","string",";",")","charinterval","ident","nontoken","("}:
                if self.la.name in {";","(",")","char","{","=","+","-","charinterval","ident","}","CHARACTERS","nontoken",".","charnumber","string"}:
                    if self.la.name in {";","(",")","char","{","=","+","-","charinterval","ident","}","nontoken",".","charnumber","string"}:
                        if self.la.name in {";","(",")","char","{","=","+","-","charinterval","ident","}","nontoken","charnumber","string"}:
                            if self.la.name in {"(",")","char","{","=","+","-","charinterval","ident","}","nontoken","charnumber","string"}:
                                if self.la.name in {"(",")","char","{","=","+","-","charinterval","ident","nontoken","charnumber","string"}:
                                    if self.la.name in {"(",")","char","=","+","-","charinterval","ident","nontoken","charnumber","string"}:
                                        if self.la.name in {"(","char","=","+","-","charinterval","ident","nontoken","charnumber","string"}:
                                            if self.la.name in {"char","=","+","-","charinterval","ident","nontoken","charnumber","string"}:
                                                if self.la.name in {"+","char","nontoken","=","charnumber","string","charinterval","ident"}:
                                                    if self.la.name in {"char","nontoken","=","charnumber","string","charinterval","ident"}:
                                                        if self.la.name in {"char","nontoken","charnumber","string","charinterval","ident"}:
                                                            if self.la.name in {"char","charnumber","string","charinterval","ident"}:
                                                                if self.la.name in {"char","charnumber","string","ident"}:
                                                                    if self.la.name in {"char","string","ident"}:
                                                                        if self.la.name in {"string","ident"}:
                                                                            if self.la.name in {"ident"}:
                                                                                self.expect("ident")
                                                                            elif self.la.name in {"string"}:
                                                                                self.expect("string")
                                                                            else: self.syn_error({'string', 'ident'})
                                                                        elif self.la.name in {"char"}:
                                                                            self.expect("char")
                                                                        else: self.syn_error({'char', 'string', 'ident'})
                                                                    elif self.la.name in {"charnumber"}:
                                                                        self.expect("charnumber")
                                                                    else: self.syn_error({'char', 'charnumber', 'string', 'ident'})
                                                                elif self.la.name in {"charinterval"}:
                                                                    self.expect("charinterval")
                                                                else: self.syn_error({'char', 'charnumber', 'string', 'charinterval', 'ident'})
                                                            elif self.la.name in {"nontoken"}:
                                                                self.expect("nontoken")
                                                            else: self.syn_error({'char', 'nontoken', 'charnumber', 'string', 'charinterval', 'ident'})
                                                        elif self.la.name in {"="}:
                                                            self.expect("=")
                                                        else: self.syn_error({'char', 'nontoken', '=', 'charnumber', 'string', 'charinterval', 'ident'})
                                                    elif self.la.name in {"+"}:
                                                        self.expect("+")
                                                    else: self.syn_error({'+', 'char', 'nontoken', '=', 'charnumber', 'string', 'charinterval', 'ident'})
                                                elif self.la.name in {"-"}:
                                                    self.expect("-")
                                                else: self.syn_error({'char', '=', '+', '-', 'charinterval', 'ident', 'nontoken', 'charnumber', 'string'})
                                            elif self.la.name in {"("}:
                                                self.expect("(")
                                            else: self.syn_error({'(', 'char', '=', '+', '-', 'charinterval', 'ident', 'nontoken', 'charnumber', 'string'})
                                        elif self.la.name in {")"}:
                                            self.expect(")")
                                        else: self.syn_error({'(', ')', 'char', '=', '+', '-', 'charinterval', 'ident', 'nontoken', 'charnumber', 'string'})
                                    elif self.la.name in {"{"}:
                                        self.expect("{")
                                    else: self.syn_error({'(', ')', 'char', '{', '=', '+', '-', 'charinterval', 'ident', 'nontoken', 'charnumber', 'string'})
                                elif self.la.name in {"}"}:
                                    self.expect("}")
                                else: self.syn_error({'(', ')', 'char', '{', '=', '+', '-', 'charinterval', 'ident', '}', 'nontoken', 'charnumber', 'string'})
                            elif self.la.name in {";"}:
                                self.expect(";")
                            else: self.syn_error({';', '(', ')', 'char', '{', '=', '+', '-', 'charinterval', 'ident', '}', 'nontoken', 'charnumber', 'string'})
                        elif self.la.name in {"."}:
                            self.expect(".")
                        else: self.syn_error({';', '(', ')', 'char', '{', '=', '+', '-', 'charinterval', 'ident', '}', 'nontoken', '.', 'charnumber', 'string'})
                    elif self.la.name in {"CHARACTERS"}:
                        self.expect("CHARACTERS")
                    else: self.syn_error({';', '(', ')', 'char', '{', '=', '+', '-', 'charinterval', 'ident', '}', 'CHARACTERS', 'nontoken', '.', 'charnumber', 'string'})
                elif self.la.name in {"TOKENS"}:
                    self.expect("TOKENS")
                else: self.syn_error({'TOKENS', 'char', '{', '=', '+', '-', '}', 'CHARACTERS', '.', 'charnumber', 'string', ';', ')', 'charinterval', 'ident', 'nontoken', '('})
            elif self.la.name in {"KEYWORDS"}:
                self.expect("KEYWORDS")
            else: self.syn_error({'TOKENS', 'char', '{', '=', '+', '-', 'KEYWORDS', '}', 'CHARACTERS', '.', 'charnumber', 'string', ';', ')', 'charinterval', 'ident', 'nontoken', '('})
        elif self.la.name in {"PRODUCTIONS"}:
            self.expect("PRODUCTIONS")
        else: self.syn_error({'TOKENS', 'char', '{', '=', '+', '-', 'KEYWORDS', '}', 'CHARACTERS', '.', 'charnumber', 'string', ';', ')', 'charinterval', 'ident', 'PRODUCTIONS', 'nontoken', '('})

