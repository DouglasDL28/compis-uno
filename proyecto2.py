import jinja2 

from scanner import Scanner
from RegularExpression import RegularExpression as RE


def generate_file(filename, data):
    # Use Jinja2 with templates and data dict to generate the html file.
    templateLoader = jinja2.FileSystemLoader(searchpath='templates/')
    env = jinja2.Environment(
        autoescape=jinja2.select_autoescape(
            # enabled_extensions=('html', 'xml'),
            default_for_string=True
        ),
        trim_blocks=True,
        lstrip_blocks=True,
        loader=templateLoader
    )

    template = env.get_template("template.txt").stream(data)
    template.dump(filename)
    

if __name__ == "__main__":
    print("PROYECTO 2")

    # TODO: leer archivo COCOL
    input_file = input("Input COCOL filename: ") or "tests/Archivo3.ATG"

    scanner = Scanner(input_file)

    compiler, characters, keywords, tokens, productions, \
        except_keywords, ignore, alphabet = scanner.scan()

    # print(keywords)
        
    re = []
    for i, name in enumerate(tokens):
        re += '('
        re += tokens[name] 
        re += ")#"
        if i < (len(tokens) - 1):
            re += "|"

    # print(re)
    # print(alphabet)

    token_names = list(tokens.keys())


    re = RE(re, alphabet=alphabet, ignore=ignore)
    dfa, elapsed_t = re.direct_construction(token_names, keywords, except_keywords)
    print("Direct Construction elapsed time: ", elapsed_t)

    # print(dfa)

    filename = input("Input filename: ") or "tests/Archivo3.ATG"
    sim, elapsed_t  = dfa.simulate(filename=filename)
    print(f"Direct Construction DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")

    generate_file(filename="lex.py", data={
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

    # dfa.simulate()


    # Generar analizador léxico