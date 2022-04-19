from scanner import Scanner


if __name__ == "__main__":
    print("Proyecto 2")

    # TODO: leer archivo COCOL
    input_file = input("Input COCOL filename: ") or "ejemploCocol.cocoL"

    scanner = Scanner(input_file)

    characters, keywords, tokens, productions = scanner.scan()

    with open("scanner.py", 'w') as scanner:
        
    for token in tokens:

    # Generar analizador léxico
    print(tokens['id'])