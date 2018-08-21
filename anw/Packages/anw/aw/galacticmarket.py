# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# galacticmarket.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The Galactic Market is an AI entity that will buy and sell resources and ships
# ---------------------------------------------------------------------------
import random
import string
import logging
from anw.func import funcs, globals

class GalacticMarket(object):
    """The Galactic Market is an AI entity that will buy and sell resources and ships"""
    def __init__(self, myGalaxy):
        logging.basicConfig(level=logging.INFO, 
        format='%(asctime)s %(levelname)s %(message)s',
        filename='galacticmarket.log',filemode='a') 
        self.log=logging.getLogger('galacticmarket')
        self.myGalaxy = myGalaxy
        self.orderVolume = {'AL':self.myGalaxy.marketOrderVolume*4.0, 'EC':self.myGalaxy.marketOrderVolume*2.0, 'IA':self.myGalaxy.marketOrderVolume}
        self.totalVolume = {'AL':0.0,'EC':0.0,'IA':0.0}
        self.setLog('Market Created')
        
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        log=logging.getLogger('galacticmarket')
        self.__dict__.update(dict)
        self.log=log
        
    def setLog(self, message):
        """Set a log message"""
        myInfo = 'galacticmarket:'
        self.log.info(myInfo+message)
        
    def doMyTurn(self):
        """Do the market round of decisions"""
        self.setLog('processing Round:%d' % self.myGalaxy.currentRound)
        self.reset()
        self.scrapeMarketActivity()
        self.setMyOrders()
    
    def reset(self):
        """Reset past rounds orders and data"""
        self.totalVolume = {'AL':0.0,'EC':0.0,'IA':0.0}
        self.removeMyPastOrders()
    
    def removeMyPastOrders(self):
        """Remove all the Market orders from previous round"""
        for id in self.myGalaxy.marketOrders.keys():
            marketOrder = self.myGalaxy.marketOrders[id]
            if marketOrder.system == 'marketSystem':
                del self.myGalaxy.marketOrders[id]
        
    def scrapeMarketActivity(self):
        """Check all the market orders currently"""
        for id, marketOrder in self.myGalaxy.marketOrders.iteritems():
            self.totalVolume[marketOrder.value] += marketOrder.amount
    
    def setMyOrders(self):
        """based on market activity and current prices send out orders into market"""
        for resource in ['AL','EC','IA']:
            orderNum = random.randint(self.myGalaxy.marketMinVolume, self.myGalaxy.marketMaxVolume)
            shift = random.choice([-1,-1,0,0,0,0,1,1,1])
            self.placeBuyOrders(resource, self.myGalaxy.prices[resource],orderNum,1,shift)
            self.placeSellOrders(resource, self.myGalaxy.prices[resource],orderNum,1,shift)
        
    def placeBuyOrders(self, resource, price, orderNum, variance, shift):
        """using a guassian distribution setup buy orders for each resource based on market activity"""         
        for i in range(orderNum):
            randomPrice = round(random.gauss(price, 1))
            if randomPrice <= 1:
                randomPrice = 1
            d = {'type':'buy-any', 'value':resource, 'min':0, 'max':randomPrice+shift, 'amount':self.orderVolume[resource], 'system':'marketSystem'}
            self.myGalaxy.genGalacticMarketOrder(d)
    
    def placeSellOrders(self, resource, price, orderNum, variance, shift):
        """using a guassian distribution setup sell orders for each resource based on market activity"""         
        for i in range(orderNum):
            randomPrice = round(random.gauss(price, 1))
            if randomPrice <= 1:
                randomPrice = 1
            d = {'type':'sell', 'value':resource, 'min':randomPrice+shift, 'max':0, 'amount':self.orderVolume[resource], 'system':'marketSystem'}
            self.myGalaxy.genGalacticMarketOrder(d)

            