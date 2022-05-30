from .lexer import Scanner
from .parser import Parser

if __name__ == "__main__":
    scanner = Scanner()
    filename = input("Enter file to compile: ") or "tests/test.txt"
    sim, token_stream, elapsed_t  = scanner.simulate(filename=filename)
    
    parser = Parser()
    parser.parse(token_stream)
    print("Compilation done.")