import os

from typing import Tuple
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import graphviz as gv

class FiniteAutomata:
    """ Finite Automata with the tuple: (Q, ∑, ∂, q_0, F). """

    def __init__(self, Q:set=set(), Sigma:set=set(), delta:dict={}, q_init=None, F:set=set()) -> None:
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_init = q_init
        self.F = F

    def simulate(self, word) -> Tuple[bool, float]:
        pass

    def plot(self, output_file='automata.png', show=False):
        """ Plots the finite automata graph. """

        G = nx.DiGraph()
        G.add_nodes_from(self.Q)
        for node, trans in self.delta.items():
            for c, s in trans.items():
                if isinstance(s, list):
                    for q in s:
                        G.add_edge(node, q, label=c)
                else:
                    G.add_edge(node, s, label=c)

        
        A = nx.nx_agraph.to_agraph(G)

        if not os.path.isdir("plots"):
            os.mkdir("plots")

        A.layout('dot')
        A.draw(f"plots/{output_file}")

        if show:
            img = mpimg.imread(f"plots/{output_file}")
            plt.imshow(img)
            plt.show()
        

    def __str__(self) -> str:

        return f"""\
Q: {self.Q}
∑: {self.Sigma}
∂: {self.delta}
q_init: {self.q_init}
F: {self.F}"""


if __name__ == "__main__":
    fa = FiniteAutomata([], [], [], "a", [])

    print(fa)
    print(fa.simulate("WSSS"))
