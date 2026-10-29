from datetime import date
class Market():

    def __init__(self,S,sigma,div,r,pricing_date= date.today(),div_time =None):
        self.S = S
        self.sigma = sigma
        self.div = div
        self.div_time = div_time
        self.r = r
        self.pricing_date =pricing_date

    def convert_div_time(self):

        return (self.div_time-self.pricing_date).days/365 if self.div_time is not None else 0 