import matplotlib.pyplot as plt
import numpy as np

class Convergence():

    def __init__(self,BS_price,I_price,pricing_times):
        self.BS_price = BS_price
        self.I_price = I_price
        self.pricing_times = pricing_times

    def Display_graph(self):

        figure,axis =  plt.subplots(figsize =(10,5))

        steps, tree_prices = zip(*[(item[1],item[0]) for item in self.I_price])

        axis.plot(steps,tree_prices, label="Tree Price")
        axis.axhline(y=self.BS_price, color = "red", linestyle ="--",label="Black scholes prices")

        axis.set_xlabel("Nb steps")
        axis.set_ylabel("Price")
        axis.set_title("Tree Pricing convergence to BS")
        axis.grid(True, alpha=0.3)
        axis.legend()
        plt.show()

        figure2 =  plt.figure(figsize =(10,5))
        
        tree_pricing_time = [item for item in self.pricing_times]
        
        plt.plot(steps,tree_pricing_time)
        
        plt.xlabel("Nb steps")
        plt.ylabel("Pricing Time")
        plt.title("Tree Pricing Time (in second)")
        plt.grid(True, alpha=0.3)

        plt.show()

        return figure, figure2

    def plot_time_vs_n(self):
        steps = np.array([item[1] for item in self.I_price], dtype=float)
        times = np.array(self.pricing_times, dtype=float)

        i0 = int(np.argmax(steps >= 10))

        fig, ax = plt.subplots(figsize=(8, 5.5))
        ax.loglog(steps, times, "o-", label=f"Temps mesuré)")

        for k, color in ((1, "tab:orange"), (2, "tab:green"), (3, "tab:red")):
            ref = times[i0] * (steps / steps[i0]) ** k  
            ax.loglog(steps, ref, "--", color=color, label=f"N^{k}")

        ax.set_title("Temps vs N")
        ax.set_xlabel("Nombre de pas N")
        ax.set_ylabel("Temps (s)")
        ax.legend()
        ax.grid(True,alpha=0.3)
        plt.show()
        return fig



    

