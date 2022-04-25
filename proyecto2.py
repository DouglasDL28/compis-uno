from scanner import Scanner
from RegularExpression import RegularExpression as RE
# from jinja2 import Environment, PackageLoader, select_autoescape

# env = Environment(
#     loader=PackageLoader("yourapp"),
#     autoescape=select_autoescape()
# )


if __name__ == "__main__":
    print("PROYECTO 2")

    # TODO: leer archivo COCOL
    input_file = input("Input COCOL filename: ") or "ejemploCocol.cocoL"

    scanner = Scanner(input_file)

    characters, keywords, tokens, productions, except_keywords = scanner.scan()

    print(keywords)

    # with open("scanner.py", 'w') as scanner:
        
    re = ""
    for i, name in enumerate(tokens):
        print(name, tokens[name])
        re += "(" + tokens[name] + ")#"
        if i < (len(tokens) - 1):
            re += "|"

    print(re)
    
    token_names = tokens.keys()

    
    # print(re)


    re = RE(re)
    dfa, elapsed_t = re.direct_construction(token_names, keywords, except_keywords)
    print("Direct Construction elapsed time: ", elapsed_t)

    filename = input("input word: ") or "tests/test.txt"
    sim, elapsed_t  = dfa.simulate(filename=filename)
    print(f"Direct Construction DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")

    # dfa.simulate()


    # Generar analizador léxico