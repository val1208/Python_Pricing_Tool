import numpy as np
from Models.BinomialTree import *
from Models.TrinomialTree import *
from Models.BlackScholes import *
from Models.MonteCarlo import *
from Datas.Market import *
def TimeToMaturity(matu,pricing_date):         
    
            return (matu - pricing_date).days / 365

def Delta(PricingMethodName,OptionParameters,MarketValues,steps=300,tree_method=True):

    delta_t = TimeToMaturity(OptionParameters.matu,MarketValues[4]) / steps
    alpha = np.exp(
                np.sqrt(3) * MarketValues[1] * np.sqrt(delta_t)
            )

    h = MarketValues[0] * (alpha - 1) if tree_method else MarketValues[0] * 0.02
    MarketData1 = Market(MarketValues[0]-h,*MarketValues[1:])
    MarketData2 = Market(MarketValues[0]+h,*MarketValues[1:])

    if (MarketValues[2] !=0 and PricingMethodName is not TrinomialTree) :
        return "No Delta for this method"

    elif( PricingMethodName in (TrinomialTree,BinomialTree)):

        Option1 = PricingMethodName(MarketData1,OptionParameters,steps)
        Option2 = PricingMethodName(MarketData2,OptionParameters,steps)

        return (Option2.BackwardPricing()-Option1.BackwardPricing())/(2*h)

    elif( PricingMethodName is BlackScholes):

        Option1 = PricingMethodName(MarketData1,OptionParameters)
        Option2 = PricingMethodName(MarketData2,OptionParameters)

        return (Option2.PricingMethod()-Option1.PricingMethod())/(2*h)
    else :
        return "No Delta for this method"

def Gamma(PricingMethodName,OptionParameters,MarketValues,steps=300,tree_method=True):

    delta_t = TimeToMaturity(OptionParameters.matu,MarketValues[4]) / steps
    alpha = np.exp(
                np.sqrt(3) * MarketValues[1] * np.sqrt(delta_t)
            )

    h = MarketValues[0] * (alpha - 1) if tree_method else MarketValues[0] * 0.02
    MarketData = Market(MarketValues[0],*MarketValues[1:])
    MarketData1 = Market(MarketValues[0]-h,*MarketValues[1:])
    MarketData2 = Market(MarketValues[0]+h,*MarketValues[1:])

    if (MarketValues[2] !=0 and PricingMethodName is not TrinomialTree) :
        return "No Gamma for this method"

    elif( PricingMethodName in (TrinomialTree,BinomialTree)):

        Option1 = PricingMethodName(MarketData1,OptionParameters,steps)
        Option2 = PricingMethodName(MarketData2,OptionParameters,steps)
        Option = PricingMethodName(MarketData,OptionParameters,steps)

        return (Option2.BackwardPricing()- 2*Option.BackwardPricing() +Option1.BackwardPricing())/(h**2)

    elif( PricingMethodName is BlackScholes):

        Option1 = PricingMethodName(MarketData1,OptionParameters)
        Option2 = PricingMethodName(MarketData2,OptionParameters)
        Option = PricingMethodName(MarketData,OptionParameters)

        return (Option2.PricingMethod()- 2*Option.PricingMethod() +Option1.PricingMethod())/(h**2)
    else :
        return "No Gamma for this method"

def Vega(PricingMethodName,OptionParameters,MarketValues,steps=300):
    sigma = MarketValues[1]
    if sigma <= 0:
        raise ValueError("Volatility must be positive to calculate Vega")

    h = sigma * 0.02
    MarketData1 = Market(MarketValues[0],sigma-h,*MarketValues[2:])
    MarketData2 = Market(MarketValues[0],sigma+h,*MarketValues[2:])

    if (MarketValues[2] != 0 and PricingMethodName is not TrinomialTree):
        return "No Vega for this method"

    elif PricingMethodName in (TrinomialTree, BinomialTree):
        Option1 = PricingMethodName(MarketData1,OptionParameters,steps)
        Option2 = PricingMethodName(MarketData2,OptionParameters,steps)

        return (Option2.BackwardPricing()-Option1.BackwardPricing())/(2*h*100)

    elif PricingMethodName is BlackScholes:
        Option1 = PricingMethodName(MarketData1,OptionParameters)
        Option2 = PricingMethodName(MarketData2,OptionParameters)

        return (Option2.PricingMethod()-Option1.PricingMethod())/(2*h*100)

    else:
        return "No Vega for this method"