import numpy as np
from Trees.Node import Node
from Trees.TrunkNode import TrunkNode


class TrinomialTree():

    def __init__(self, marketdata, option, steps):
        self.marketdata = marketdata
        self.option = option
        self.steps = steps

        self.div = marketdata.div
        self.t_ex = marketdata.convert_div_time()

        self.delta_t = option.TimeToMaturity(self.marketdata.pricing_date) / steps

        self.forward_factor = np.exp(marketdata.r * self.delta_t)

        self.alpha = np.exp(
            np.sqrt(3) * self.marketdata.sigma * np.sqrt(self.delta_t)
        )

        # Probabilités
        c = np.exp(self.marketdata.sigma**2 * self.delta_t) - 1

        self.pd = c / ((1 - self.alpha) * (self.alpha**-2 - 1))
        self.pu = self.pd / self.alpha
        self.pm = 1 - self.pu - self.pd

        self.root = TrunkNode(self.marketdata.S, self)

        self.is_american = self.option.is_american
        self.negative_expectation_prunings = 0
        self.boundary_fallbacks = 0

        self.zero_node = Node(0, self)
        self.zero_node.up = self.zero_node
        self.zero_node.down = self.zero_node
        self.zero_node.previous = None
        self.zero_node_for_step = None

        self.BuildTree()
        self.zero_terminal = self.zero_node

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Verif des divs moments et probas ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~é

    def _div_in_step(self, i):
        #on verif comme dans slide 23 : falls between the current date (excluded) and the next one (included)

        eps = self.delta_t * 1e-3
        t0 = i * self.delta_t
        t1 = (i + 1) * self.delta_t

        return self.div > 0 and t0 + eps < self.t_ex <= t1 + eps

    def _moments(self, S, i):
        sig2 = self.marketdata.sigma ** 2
        c = np.exp(sig2 * self.delta_t) - 1

        E = S * self.forward_factor
        base = S

        if self._div_in_step(i):
            t1 = (i + 1) * self.delta_t

            E -= self.div * np.exp(self.marketdata.r * (t1 - self.t_ex))

            base = S - ((t1 - self.t_ex) / self.delta_t) * self.div

        V = (base * self.forward_factor) ** 2 * c

        return E, V

    def _set_probas(self, node, p, i):
        E, V = self._moments(node.price, i)
        if E <= 0:
            #si esperance negative on garde une proba a 100% de rester a zero
            node.next_mid = self.zero_node_for_step
            node.probas = (0.0, 1.0, 0.0)
            self.negative_expectation_prunings += 1
            return

        probabilities = self._probas(E, V, p.price)
        node.probas = probabilities


    #sans div on sait que le mid est égal au forward donc pu pm et pd sont simplifié 
    #cest ceux quon met dans le init
    #par contre pour le cas des divs on a ces formules la : 

    def _probas(self, E, V, S_mid):
        a = self.alpha
        diff = E - S_mid
        e_m1 = diff / S_mid                           
        w_m1 = (V + diff * (E + S_mid)) / S_mid ** 2   

        pd = (w_m1 - (a + 1) * e_m1) / ((1 - a) * (a ** -2 - 1))
        pu = (e_m1 - (1 / a - 1) * pd) / (a - 1)
        pm = 1 - pd - pu

        return (pd, pm, pu)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ construction ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def BuildTree(self):

        trunk = self.root
        n_up = 0
        n_down = 0

        for i in range(self.steps):
            trunk, n_up, n_down = self._next_column(
                trunk, i, n_up, n_down
            )

    #permet de verifier l'index (par rapport au trunk) du mid qui correspond au forward d'un certain noeud
    #c'est nécéssaire car quand il y a des divs les enfants de 2 noeuds ne vont pas forcement se rejoindre
    #tandis que quand il n'y a pas de div le fils up down = fils down up donc on connait déja la dimension de la colonne suivante
    def _mid_index(self, S, i, trunk_next_price):

        E, _ = self._moments(S, i)
        return round(np.log(E / trunk_next_price) / np.log(self.alpha))

    def _column_nodes(self, trunk):
        yield trunk
        node = trunk.up
        while node is not None:
            yield node
            node = node.up
        node = trunk.down
        while node is not None:
            yield node
            node = node.down

    def _next_column(self, trunk, i, n_up, n_down):
        next_zero_node = Node(0, self)
        next_zero_node.up = next_zero_node
        next_zero_node.down = next_zero_node
        next_zero_node.previous = self.zero_node

        self.zero_node.next_mid = next_zero_node
        self.zero_node_for_step = next_zero_node

        E_trunk, _ = self._moments(trunk.price, i)
        target_indices = None
        if self._div_in_step(i):
            expectations = [self._moments(node.price, i)[0]for node in self._column_nodes(trunk)]

            positive_expectations = [E for E in expectations if E > 0]

            if E_trunk > 0:
                next_trunk_price = E_trunk
            elif positive_expectations:
                next_trunk_price = float(np.median(positive_expectations))
            
        else:
            next_trunk_price = E_trunk

        next_trunk = TrunkNode(next_trunk_price, self)

        trunk.next = next_trunk
        next_trunk.previous = trunk

        # Taille de la colonne suivante
        if self._div_in_step(i):
            target_indices = [round(np.log(E / next_trunk_price) / np.log(self.alpha))for E in positive_expectations]
            if not target_indices:
                target_indices = [0]

            lowest_target = min(target_indices)
            highest_target = max(target_indices)
            new_up = highest_target + 1
            new_down = 1 - lowest_target

        else:

            new_up = n_up + 1
            new_down = n_down + 1

        self._build_column(next_trunk,new_up,new_down)

        self._link_column(trunk, next_trunk, i)
        self.zero_node = next_zero_node

        return next_trunk, new_up, new_down

    def _build_column(self, trunk, n_up, n_down):

        node = trunk

        #par rapport au trunk on sait que tous nos voisins (les autres noeuds de la meme colonne)
        #  seront a trunk *alpha^k ou trunk/alpha^k du trunk
        for _ in range(n_up):

            new = Node(node.price * self.alpha,self)

            node.up = new
            new.down = node

            node = new

        node = trunk

        for _ in range(n_down):

            new = Node(node.price / self.alpha,self)

            node.down = new
            new.up = node

            node = new

    #on va synchroniser pour chaque noeud son fils mid 
    def _link_column(self, trunk, next_trunk, i):
        div = self._div_in_step(i)

        trunk.next_mid = next_trunk
        if div:
            self._set_probas(trunk, next_trunk, i)

        #j cest la hauteur au sein d'une meme colonne par rapport au trunk
        # et notre but cest de trouver le bon p_idx correspondant au mid d'en face de chaque j 
        for direction, j_sign in ((lambda n: n.up, 1),(lambda n: n.down, -1)):
            node = direction(trunk)
            j = 0

            p = next_trunk
            p_idx = 0
            while node is not None:
                j += j_sign
                # S'il y a un dividende, on cherche
                # le mid correspondant sinon le mid correspondant cest juste le fils en face 
                if div:
                    E, _ = self._moments(node.price, i)
                    if E <= 0:
                        self._set_probas(node, None, i)
                        node = direction(node)
                        continue
                    m = self._mid_index(node.price, i, next_trunk.price)
                else:
                    m = j

                while p_idx < m:
                    p = p.up
                    p_idx += 1

                while p_idx > m:
                    p = p.down
                    p_idx -= 1

                node.next_mid = p
                if div:
                    self._set_probas(node, p, i)

                node = direction(node)


    def _node_value(self, node):

        if node.probas is None:
            pd = self.pd
            pm = self.pm
            pu = self.pu
        else:
            pd, pm, pu = node.probas

        m = node.next_mid

        cont = self.df * (
            pu * m.up.value
            + pm * m.value
            + pd * m.down.value
        )

        return cont

    def _update_value(self, node):
        if self.option.option_type.upper() in ("ONE_TOUCH_CALL", "ONE_TOUCH_PUT"):
            if self.option._IsOneTouchHit(node):
                return self.option.cash
            return self._node_value(node)
        
        continuation = self._node_value(node)
        if self.is_american:
            return max(continuation, self.option._SetPayoff(node))
        return continuation

    def BackwardPricing(self):
        self.df = np.exp(-self.marketdata.r * self.delta_t)

        trunk = self.root
        while trunk.next is not None:
            trunk = trunk.next

        # payoffs terminaux
        trunk.value = self.option._SetPayoff(trunk)
        node = trunk.up
        while node is not None:
            node.value = self.option._SetPayoff(node)
            node = node.up
        node = trunk.down
        while node is not None:
            node.value = self.option._SetPayoff(node)
            node = node.down
        zero_node = self.zero_terminal
        zero_node.value = self.option._SetPayoff(zero_node)

        # backward
        i = self.steps
        while trunk.previous is not None:
            trunk = trunk.previous
            i -= 1
            zero_node = zero_node.previous

            node = trunk.up
            while node is not None:
                node.value = self._update_value(node)
                node = node.up

            node = trunk.down
            while node is not None:
                node.value = self._update_value(node)
                node = node.down

            trunk.value = self._update_value(trunk)
            zero_node.value = self._update_value(zero_node)

        return self.root.value

  