# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# order.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an Order
# ---------------------------------------------------------------------------
import anwp.func.root

class Order(anwp.func.root.Root):
    """An Order Represents a general order given by a player"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.type = str() # type of order Add, Upgrade, Remove, etc..
        self.value = str() # order value
        self.round = int() # round order was given
        self.defaultAttributes = ('id', 'type', 'value', 'round')
        self.setAttributes(args)

class IndustryOrder(Order):
    """An Industry Order includes the system the order was given for"""
    def __init__(self, args):
        Order.__init__(self, args)
        self.system = str() # System ID of order
        self.defaultAttributes = ('id', 'type', 'value', 'round', 'system')
        self.setAttributes(args)

class MarketOrder(Order):
    """An Market Order represents an order to buy/sell resources on the galactic market"""
    def __init__(self, args):
        Order.__init__(self, args)
        self.system = str() # System ID of order
        self.min = float() # minimum bid
        self.max = float() # maximum bid
        self.amount = float() # amount to buy/sell        
        self.amountUsed = float() # actual amount bought/sold
        self.defaultAttributes = ('id', 'type', 'value', 'round', 'system',
                                  'min', 'max', 'amount', 'amountUsed')
        self.setAttributes(args)
    
    def cleanUp(self):
        """Clear order data from previous round"""
        if self.amountUsed > 0:
            self.amount -= self.amountUsed
            self.amountUsed = 0
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_order.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        