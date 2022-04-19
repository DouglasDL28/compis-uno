from RegularExpression import RegularExpression

if __name__ == "__main__":
    re = input("Ingrese la expresión regular: ") or "(a|b)*a(a|b)(a|b)"
    word = input("Ingrese la palabra a evaluar: ") or "01111"

    re = RegularExpression(re)

    # Thompson
    print("--------THOMPSON--------")
    thompson, thompson_elapsed = re.Thompson()
    print("Thompson elapsed time: ", thompson_elapsed)
    thompson.plot_fa("Thompson.png")

    sim, elapsed = thompson.fa.simulate(word)
    print(f"Thompson NFA simulation: {sim} -- elapsed time: {elapsed}\n")
    
    # Subset
    print("--------SUBSETS--------")
    subset_dfa, elapsed_t = re.thompson_nfa.subset_construction()
    print("Subset construction elapsed time: ", elapsed_t)

    subset_dfa.plot("SubsetConstruction.png")

    sim, elapsed_t  = subset_dfa.simulate(word)
    print(f"Subset DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")

    # Direct
    print("--------DIRECT--------")
    dfa, elapsed_t = re.direct_construction()
    print("Direct Construction elapsed time: ", elapsed_t)

    dfa.plot("Directo.png")

    sim, elapsed_t  = subset_dfa.simulate(word)
    print(f"Direct Construction DFA simulation: {sim} -- elapsed time: {elapsed_t}\n")


