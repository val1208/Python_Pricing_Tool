import numpy as np

class MonteCarlo:
    def __init__ (self,marketdata,nb_path,option,random_numbers=None):
        self.marketdata =marketdata
        self.nb_path = nb_path
        self.option =option
        self.random_numbers = random_numbers

    def PricingMethod(self):

        if(self.nb_path <=0 ):
            raise ValueError("Nb_path must be positive")
        if self.random_numbers is not None and len(self.random_numbers) != self.nb_path:
            raise ValueError("random_numbers length must match nb_path")

        S = self.marketdata.S
        r = self.marketdata.r
        sigma = self.marketdata.sigma

        K = self.option.K
        T=self.option.TimeToMaturity(self.marketdata.pricing_date)
        option_type = self.option.option_type
        payoff_sum =0

        for i in range(self.nb_path):
            Z = np.random.randn() if self.random_numbers is None else self.random_numbers[i]
            S_i = S*np.exp((r -0.5* sigma**2)*T + sigma*np.sqrt(T)*Z)

            if(option_type.upper()=="CALL"):
                payoff = max(S_i-K,0)
            elif (option_type.upper()=="PUT"):
                payoff = max(K-S_i,0)
            else :
                raise ValueError("Option type must be call or put")


            payoff_sum += payoff

        return np.exp(-r*T)*payoff_sum/self.nb_path


