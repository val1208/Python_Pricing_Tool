import numpy as np
import scipy.stats as stats

class BlackScholes:
    def __init__(self,marketdata, option):
        self.marketdata = marketdata
        self.option = option

    def d1(self):
        S = self.marketdata.S
        r = self.marketdata.r
        sigma = self.marketdata.sigma

        K = self.option.K
        T=self.option.TimeToMaturity(self.marketdata.pricing_date)

        if(K <= 0 or sigma <=0):
            raise ValueError("Your param must be positive")

        return (np.log(S/K) + (r + sigma**2/2)*T)/(sigma *np.sqrt(T))
    
    def d2(self):
        sigma = self.marketdata.sigma

        T=self.option.TimeToMaturity(self.marketdata.pricing_date)

        return self.d1() -sigma*np.sqrt(T)

    def PricingMethod(self):
        if not isinstance(self.option.option_type,str):
            raise TypeError("option type must be a call or a put")

        S = self.marketdata.S
        r = self.marketdata.r

        K = self.option.K
        T=self.option.TimeToMaturity(self.marketdata.pricing_date)

        if self.option.option_type.upper() == "CALL":
            return S *stats.norm.cdf(self.d1()) -K*np.exp(-r*T)*stats.norm.cdf(self.d2())

        elif self.option.option_type.upper() =="PUT":
            return K*np.exp(-r*T)*stats.norm.cdf(-self.d2()) - S*stats.norm.cdf(-self.d1())
        else :
            return ("Wrong option type")
         

    