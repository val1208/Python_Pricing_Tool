from Models.BlackScholes import *
from Datas.Option import *
from Models.MonteCarlo import *
from Datas.Market import *
from Models.BinomialTree import *
from Stats.Graphs import *
from datetime import date
import time
from math import log10
import matplotlib.pyplot as plt
from Models.TrinomialTree import *
from Stats.Greeks import *


if __name__ =="__main__":

    #Params
    # MarketData = Market(100,0.2,0,0.03)
    # MarketDataWithDiv = Market(100,0.2,4,0.03,date(2027,8,30))

    # AmericanCallOptionParameters = Option(101,date(2027,9,30),"call",is_american = True)
    # CallOptionParameters = Option(101,date(2027,9,30),"call")
    # PutOptionParameters = Option(100,date(2027,9,30),"put")  

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Theorical Prices~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~éé
    #Prix théoriques avec BS
    # CallBSOption = BlackScholes(MarketData,CallOptionParameters)
    # PutBSOption = BlackScholes(MarketData,PutOptionParameters)

    # # #Prix avec MC
    # CallMCOption = MonteCarlo(MarketData,100_000,CallOptionParameters)
    # PutMCOption = MonteCarlo(MarketData,100_000,PutOptionParameters)


    # PutOptionBSPrice = PutBSOption.PricingMethod()
    # CallOptionBSPrice = CallBSOption.PricingMethod()
    # print("Prix BS d'un Call :", CallOptionBSPrice) 
    # print("Prix BS d'un Put :", PutOptionBSPrice)

    # PutOptionMCPrice = PutMCOption.PricingMethod()
    # CallOptionMCPrice = CallMCOption.PricingMethod()
    # print("Prix MC d'un Call :", CallOptionMCPrice) 
    # print("Prix MC d'un Put :", PutOptionMCPrice)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Trees ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
    # CallOptionTree = BinomialTree(MarketData,CallOptionParameters,2)
    # priceCall = CallOptionTree.BackwardPricing()

    # PutOptionTree = BinomialTree(MarketData,PutOptionParameters,2)
    # pricePut =PutOptionTree.BackwardPricing()


    # print(f"Prices of your call with Backward method is : ", priceCall)
    # print(f"Prices of your put with Backward method is : ", pricePut)


    # TrinomialCallOptionTree = TrinomialTree(MarketData,CallOptionParameters,1000)
    # TrinomialCallPrice = TrinomialCallOptionTree.BackwardPricing()
    # print(f"Prices of your Trinomial call with Backward method is : ", TrinomialCallPrice)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
    # prices = []
    # pricing_times = []
    # nb_step =100
    # nb_points = 100
    # steps = sorted({round(10 ** (j * log10(nb_step) / (nb_points - 1))) for j in range(nb_points)})
    
    # for i in steps:
    #     start = time.perf_counter()
    #     CallOptionTree = BinomialTree(MarketData,CallOptionParameters,i)
    #     price = CallOptionTree.BackwardPricing()
    #     end = time.perf_counter() -start

    #     prices.append([price,i])
    #     pricing_times.append(end)


    # Graph1 = Convergence(CallOptionBSPrice, prices, pricing_times)
    # Graph1.Display_graph()
    # Graph1.plot_time_vs_n()

   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  Greeks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #espace examen
    MarketDataWithDiv = Market(100.15,0.26,2.9,0.038,date(2026,10,28),date(2027,6,9))
    MarketValues = (100.15,0.26,2.9,0.038,date(2026,10,28),date(2027,6,9))

    DigitalOptionParameters = Option(
        95,
        date(2027,8,27),
        "PUT",
        is_american=True
    )

    # True: bump based on the tree spacing; False: bump by 2% of spot.
    tree_method = True

    TrinomialDigitalOptionTree = TrinomialTree(
        MarketDataWithDiv, DigitalOptionParameters, 300
    )
    TrinomialDigitalPrice = TrinomialDigitalOptionTree.BackwardPricing()


    print("Trinomial digital call price:", TrinomialDigitalPrice)
    print("Delta of trinomial",Delta(TrinomialTree,DigitalOptionParameters,MarketValues,300,tree_method=tree_method,))
    print("Gamma of trinomial",Gamma(TrinomialTree,DigitalOptionParameters,MarketValues,300,tree_method=tree_method,))
    print("Vega of trinomial",Vega(TrinomialTree, DigitalOptionParameters, MarketValues, 300))

    # print("Delta of trinomial call is ", Delta(TrinomialTree,CallOptionParameters,MarketValues,300))
    # print("Delta of binomial call is ", Delta(BinomialTree,CallOptionParameters,MarketValues,300))
    # print("Delta of BS call is ", Delta(BlackScholes,CallOptionParameters,MarketValues))
    # print("Delta of MonteCarlo call is ", Delta(MonteCarlo,CallOptionParameters,MarketValues))




    