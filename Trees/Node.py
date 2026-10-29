import numpy as np

class Node():
    def __init__(self,price,tree):
        self.price = price
        self.tree = tree
        
        self.value = None
        self.up = None
        self.down = None

        #le fils du milieu (normalement égal au forward ou au moins au noeud le plus proche du forward)
        self.next_mid = None 
        self.probas = None

