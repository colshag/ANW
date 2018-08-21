# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# marketsystemsellvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to modify the
# system resource selling orders for the galactic market
# ---------------------------------------------------------------------------
from rootbutton import RootButton
from anw.gui import valuebar, textonscreen
from anw.func import globals

class MarketSystemSellValue(RootButton):
    """The System Market Gui for setting a price and amount to sell a resource from a system"""
    def __init__(self, path, mySystemDict, resource, currentPrice):
        self.mySystemDict = mySystemDict
        self.resource = resource
        self.currentPrice = currentPrice
        self.maxPrice = currentPrice
        self.maxPriceIncrease = self.maxPrice*2.0
        y = -0.4
        x = 0.65
        RootButton.__init__(self, path, x=x, y=y, name='sys_sell')
        self.allKeys = ['A','S','D','F','G','Z','X','C','V']
        self.scale = 0.25
        self.priceBar = None
        self.amountBar = None
        self.maxAmount = mySystemDict[resource]
        self.currentAmount = mySystemDict[resource]
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S','F','G','Z','X','C','V']
        self.scrollFactor = 0
        self.focus = 'price'
        self.pressButton('G')
        self.pressButton('V')
        self.myTitle = 'Set Price and Amount to Sell on Market:'
        self.createTitleCard('marketTitle','Create Sell Order for %s:' % self.resource,
                         30,x-0.04, y+0.35)
        self.createPriceBar()
        self.createAmountBar()
        self.enableSubmit()
                
    def createPriceBar(self):
        """Market Price from 0 to Max"""
        self.priceBar = valuebar.ValueBar(self.path, scale=self.scale, extraText = ' CREDITS PER UNIT', showOverValues=1)
        self.priceBar.setMyValues(self.currentPrice, self.maxPrice)
        self.priceBar.setMyPosition(self.posInitX+0.20, 0, self.posInitY+0.31)
        color = globals.resourceColors['CR']
        self.priceBar.setColor(globals.colors[color])
        self.myWidgets.append(self.priceBar)
    
    def createAmountBar(self):
        """Market Amount from 0 to Max"""
        self.amountBar = valuebar.ValueBar(self.path, scale=self.scale, extraText = ' %s' % self.resource, showOverValues=0)
        self.amountBar.setMyValues(self.currentAmount, self.maxAmount)
        barHeight = self.amountBar.myBar.getHeight()*self.scale
        self.amountBar.setMyPosition(self.posInitX+0.20, 0, self.posInitY+0.31-barHeight)
        color = globals.resourceColors[self.resource]
        self.amountBar.setColor(globals.colors[color])
        self.myWidgets.append(self.amountBar)
    
    def setValue(self, value):
        """Set either the price or the amount"""
        if self.focus == 'price':
            self.setPrice(value)
        else:
            self.setAmount(value)
        self.enableSubmit()
    
    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.currentAmount > 0 and self.currentPrice > 0:
            self.enableButton('S')
        else:
            self.disableButton('S')
        
    def setPrice(self, value):
        """Update priceBar amount by value"""
        validValue = self.getValidValue(value, self.currentPrice, self.maxPriceIncrease)
        self.currentPrice = validValue
        self.priceBar.setMyValues(self.currentPrice, self.maxPrice)
        color = globals.resourceColors['CR']
        self.priceBar.setColor(globals.colors[color])
        self.priceBar.setMyPosition(self.priceBar.x,self.priceBar.y,self.priceBar.z)
        self.enableButton('S')
    
    def setAmount(self, value):
        """Update Amount Bar by value"""
        validValue = self.getValidValue(value, self.currentAmount, self.maxAmount)
        self.currentAmount = validValue
        self.amountBar.setMyValues(self.currentAmount, self.maxAmount)
        color = globals.resourceColors[self.resource]
        self.amountBar.setColor(globals.colors[color])
        self.enableButton('S')
    
    def getValidValue(self, value, current, maxValue):
        """if value being submitted is too big or too small for max
        or min value then set value to max or min value"""
        newValue = current + value
        if value > 0:#trying to add
            if newValue > maxValue:
                return maxValue
            else:
                return newValue
        else:# trying to remove
            if newValue < 1:
                return 0
            else:
                return newValue
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        x = 0
        y = 1
        for key in ['Z','X','C','V']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        x = 0
        y = 2
        for key in ['A','S','D','F','G']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        y = 0
            
    def pressS(self):
        """Submit value to server"""
        d = {'type':'sell', 'value':self.resource, 'min':self.currentPrice, 'max':0, 'amount':self.currentAmount, 'system':self.mySystemDict['id']}
        self.mode.submitMarketOrder(d)
    
    def pressD(self):
        """Increment Value"""
        self.setValue(self.scrollFactor)
    
    def pressA(self):
        """Decrement Value"""
        self.setValue(-self.scrollFactor)
   
    def pressZ(self):
        """Set scroll factor to 1"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.scrollFactor = 1
    
    def pressX(self):
        """Set scroll factor to 5"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.pressButton('G')
        self.scrollFactor = 10
    
    def pressC(self):
        """Set scroll factor to 100"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.pressButton('G')
        self.scrollFactor = 100
    
    def pressV(self):
        """Set scroll factor to 1000"""
        self.enableLastButton('V')
        self.disableButton('V')
        self.pressButton('G')
        self.scrollFactor = 1000
    
    def pressF(self):
        """Set focus to price"""
        self.enableLastButton2('F')
        self.disableButton('F')
        self.focus = 'price'
        self.pressButton('Z')
        
    def pressG(self):
        """Set focus to amount"""
        self.enableLastButton2('G')
        self.disableButton('G')
        self.focus = 'amount'
    
class MarketSystemBuyValue(MarketSystemSellValue):        
    def __init__(self, path, mySystemDict, resource, currentPrice):
        self.mySystemDict = mySystemDict
        self.resource = resource
        self.currentPrice = currentPrice
        self.maxPrice = currentPrice
        self.maxPriceIncrease = self.maxPrice*4.0
        y = -0.4
        x = -1.03
        RootButton.__init__(self, path, x=x, y=y, name='sys_buy')
        self.allKeys = ['A','S','D','F','G','Z','X','C','V']
        self.scale = 0.25
        self.priceBar = None
        self.amountBar = None
        self.maxAmount = 20000.0
        self.currentAmount = 0.0
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S','F','G','Z','X','C','V']
        self.scrollFactor = 0
        self.focus = 'price'
        self.pressButton('G')
        self.pressButton('V')
        self.myTitle = 'Set Price and Amount to Buy on Market:'
        self.createTitleCard('marketTitle','Create Buy Order for %s:' % self.resource,
                         30,x-0.04, y+0.35)
        self.createPriceBar()
        self.createAmountBar()
        self.enableSubmit()

    def pressS(self):
        """Submit value to server"""
        d = {'type':'buy-any', 'value':self.resource, 'min':0, 'max':self.currentPrice, 'amount':self.currentAmount, 'system':self.mySystemDict['id']}
        self.mode.submitMarketOrder(d)
        
if __name__ == "__main__":
    systemDict = {'id':'1','AL':1200, 'EC':110, 'IA':330, 'name':'SystemName1'}
    myValue = MarketSystemSellValue('media', systemDict, 'EC', 20.0, 20.0)
    run()