
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
        self.Expr()

    def Expr(self):
        while self.la.name in {"(","-","number"}:
            self.Stat()
            self.expect(";")
            while self.la.name in {"white"}:
                self.expect("white")
        while self.la.name in {"white"}:
            self.expect("white")
        self.expect(".")

    def Stat(self):
        value=0;
        value = self.Expression(value)
        print(str(value));

    def Expression(self, result):
        result1,result2=0,0;
        result1 = self.Term(result1)
        while self.la.name in {"+","-"}:
            if self.la.name in {"+"}:
                self.expect("+")
                result2 = self.Term(result2)
                result1+=result2;
            elif self.la.name in {"-"}:
                self.expect("-")
                result2 = self.Term(result2)
                result1-=result2;
            else: self.syn_error({'+', '-'})
        result=result1;
        return result

    def Term(self, result):
        result1,result2=0,0;
        result1 = self.Factor(result1)
        while self.la.name in {"*","/"}:
            if self.la.name in {"*"}:
                self.expect("*")
                result2 = self.Factor(result2)
                result1*=result2;
            elif self.la.name in {"/"}:
                self.expect("/")
                result2 = self.Factor(result2)
                result1/=result2;
            else: self.syn_error({'*', '/'})
        result=result1;
        return result

    def Factor(self, result):
        signo=1;
        if self.la.name in {"-"}:
            self.expect("-")
            signo=-1;
        if self.la.name in {"number"}:
            result = self.Number(result)
        elif self.la.name in {"("}:
            self.expect("(")
            result = self.Expression(result)
            self.expect(")")
        else: self.syn_error({'(', 'number'})
        result*=signo;
        return result

    def Number(self, result):
        self.expect("number")
        result=int(self.t.lexeme)
        return result

