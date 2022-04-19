if __name__ == "__main__":
    print("Proyecto 2")

    # TODO: leer archivo COCOL
    input_file = input("Input COCOL filename: ") or "ejemploCocol.cocoL"

    file = open(input_file, "r").read()

    for index, char in enumerate(file):
        print(file[index])
    # Generar analizador léxico
    # 