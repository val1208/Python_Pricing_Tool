import numpy as np
from Trees.Node import *
from Trees.TrunkNode import *

class BinomialTree():
    def __init__(self,marketdata,option,steps):
        self.marketdata = marketdata
        self.option = option
        self.steps = steps

        self.delta_t = option.TimeToMaturity(self.marketdata.pricing_date)/steps
        self.forward_factor = np.exp(marketdata.r * self.delta_t)
        self.alpha = ((1+np.exp(self.marketdata.sigma**2 * self.delta_t))/2
                      +np.sqrt(((1+(np.exp(self.marketdata.sigma**2 * self.delta_t)))/2)**2 -1))**2

        self.root = TrunkNode(self.marketdata.S,self)
        
        self.u = 1/(1+np.sqrt(self.alpha))
        self.d= 1 -self.u    

        self.is_american = self.option.is_american

        self.BuildTree()    


    def BuildTree(self):

        self.BuildBranch(
            self.root
        )

    def TrunkForward(self, trunk):

        new_price = trunk.price *self.forward_factor
        new_trunk = TrunkNode(new_price,self)

        trunk.next = new_trunk
        new_trunk.previous = trunk

        return new_trunk

    def BuildBranch(self,trunk):

        for step in range(1,self.steps+1):

            trunk = self.TrunkForward(trunk)
            self.AddChildren(trunk,step)

    def AddChildren(self,trunk,step):

        sqrt_alpha = np.sqrt(self.alpha)

        if step %2!=0 :
            up_Node = Node(trunk.price*sqrt_alpha,self)
            down_Node = Node(trunk.price/sqrt_alpha,self)

            trunk.up = up_Node
            trunk.down = down_Node

            up_Node.up = None
            up_Node.down = trunk

            down_Node.up = trunk
            down_Node.down = None
        else :
            up_Node = trunk
            down_Node = trunk

        for _ in range(step//2):

            new_up = Node(up_Node.price*sqrt_alpha**2,self)
            new_down = Node(down_Node.price/sqrt_alpha**2,self)
       
            new_down.up = up_Node
            new_up.down = down_Node

            up_Node.up = new_up
            up_Node = new_up

            down_Node.down = new_down   
            down_Node = new_down

    

    def BackwardPricing(self):
        discount_factor = np.exp(-self.marketdata.r * self.delta_t)
        terminal_step = self.steps
        trunk = self.root

        while trunk.next is not None:
            trunk = trunk.next

        #on calcule tous les payoff terminaux, dabord le trunk ensuite tous les
        #noeuds du dessus et ensuite les noeuds en dessous
        if terminal_step % 2 == 0:
            trunk.value = self.option._SetPayoff(trunk)

        node = trunk.up
        while node is not None:
            node.value = self.option._SetPayoff(node)
            node = node.up

        node = trunk.down
        while node is not None:
            node.value = self.option._SetPayoff(node)
            node = node.down

        #maintenant on descend d'un cran aec trunk.previous
        #trunk.previous va alors utiliser les valeurs des noeuds de trunk 

        while trunk.previous is not None:
            next_trunk = trunk
            trunk = trunk.previous

            #on fait le step -1 car on va se placer dans la branche "previous"
            #MAIS utiliser les valeurs des noeuds de la branche au dessus de nous
            #exemple on est au temps 3 sur 3 mais on va se placer au temps 2
            #en utilisant les valeurs des noeuds au temps 3
            terminal_step -= 1

            #on gere le cas ou le pas est pair cest a dire qu'il y a un 
            # trunk au milieu de la branche a calculer
            if terminal_step % 2 == 0:
                #pareil qu'au début, on gere tous les noeuds du dessus du trunk
                node = trunk.up

                next_node = next_trunk.up
                while node is not None:


                    continuation_value = discount_factor * (
                        self.u * next_node.up.value
                        + self.d * next_node.value
                    )

                    if self.is_american :
                        intrinsic_value = self.option._SetPayoff(node)
                        node.value = max(intrinsic_value,continuation_value)
                    else : 
                        node.value = continuation_value

                    node = node.up
                    next_node = next_node.up

                #ici les noeuds en dessous
                node = trunk.down
                next_node = next_trunk.down
                while node is not None:
                    continuation_value = discount_factor * (
                        self.u * next_node.value
                        + self.d * next_node.down.value
                    )

                    if self.is_american :                    
                        intrinsic_value = self.option._SetPayoff(node)
                        node.value = max(intrinsic_value,continuation_value)
                    else : 
                        node.value = continuation_value

                    node = node.down
                    next_node = next_node.down

                #on finit par la valeur du trunk (qui est ici le previous trunk)
                continuation_value = discount_factor * (
                    self.u * next_trunk.up.value
                    + self.d * next_trunk.down.value
                )

                if self.is_american :            
                    intrinsic_value = self.option._SetPayoff(trunk)
                    trunk.value = max(intrinsic_value,continuation_value)
                else : 
                    trunk.value = continuation_value
            else:
                #maintenant on se place dans le cas ou notre branche previous est 
                # un cas Impair
                #a savoir que si notre branche previous est impair
                #alors la branche d'au dessus va etre composée d'un noeud au milieu qui est le trunk
                node = trunk.up
                next_node = next_trunk.up
                lower_node = next_trunk
                while node is not None:
                    continuation_value = discount_factor * (
                        self.u * next_node.value
                        + self.d * lower_node.value
                    )

                    if self.is_american :          
                        intrinsic_value = self.option._SetPayoff(node)
                        node.value = max(intrinsic_value,continuation_value)
                    else : 
                        node.value = continuation_value
                    
                    node = node.up
                    lower_node = next_node
                    next_node = next_node.up

                node = trunk.down
                next_node = next_trunk.down
                upper_node = next_trunk
                while node is not None:
                    continuation_value = discount_factor * (
                        self.u * upper_node.value
                        + self.d * next_node.value
                    )

                    if self.is_american :            
                        intrinsic_value = self.option._SetPayoff(node)
                        node.value = max(intrinsic_value,continuation_value)
                    else : 
                        node.value = continuation_value

                    node = node.down
                    upper_node = next_node
                    next_node = next_node.down

        return self.root.value



            




          