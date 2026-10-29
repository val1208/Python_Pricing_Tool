from Trees.Node import *

class TrunkNode(Node):
     def __init__(self, price, tree):
        super().__init__(price, tree)

        self.next = None
        self.previous = None
