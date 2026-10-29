from datetime import date

class Option:
    def __init__(self,K,matu,option_type,is_american=False,cash=1.0):
        self.matu = matu
        self.K = K
        self.option_type = option_type
        self.is_american = is_american
        self.cash = cash

        if self.cash < 0:
            raise ValueError("Cash payout must be non-negative")

    def TimeToMaturity(self,pricing_date):
            maturity = self.matu
    
            return (maturity - pricing_date).days / 365


    def _IsOneTouchHit(self,node):
        option_type = self.option_type.upper() 
        if (option_type == "ONE_TOUCH_CALL"):
            return node.price >= self.K
        if (option_type =="ONE_TOUCH_PUT"):
            return node.price <= self.K
        return False

    def _SetPayoff(self, node):
        option_type = self.option_type.upper()

        if option_type == "CALL":
            return max(node.price - self.K, 0)
        elif option_type == "PUT":
            return max(self.K - node.price, 0)
        elif option_type == "DIGITAL_CALL":
            return self.cash if node.price > self.K else 0
        elif option_type == "DIGITAL_PUT":
            return self.cash if node.price < self.K else 0
        elif option_type == "ONE_TOUCH_CALL":
            return self.cash if self._IsOneTouchHit(node) else 0
        elif option_type == "ONE_TOUCH_PUT":
            return self.cash if self._IsOneTouchHit(node) else 0

        raise ValueError(
            "Option type must be CALL, PUT, DIGITAL_CALL, DIGITAL_PUT, "
            "ONE_TOUCH_CALL, or ONE_TOUCH_PUT"
        )
        
