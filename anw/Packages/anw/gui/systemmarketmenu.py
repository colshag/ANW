# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# systemmarketmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to choose from various market choices
# ---------------------------------------------------------------------------
from rootbutton import RootButton
from anw.gui import systemresources
import string

class SystemMarketMenu(RootButton):
    """The System Market Menu Gui"""
    def __init__(self, path, mySystemDict, x=-0.25, y=-0.1):
        RootButton.__init__(self, path, x=x, y=y, name='market')
        self.mySystemDict = mySystemDict
        self.scale = 0.25
        self.createMySystemResources()
        
    def createMySystemResources(self):
        self.mySystemResources = systemresources.SystemResources(self.path, self.posInitX+0.65, self.posInitY+0.45, 
                                                                 self.mySystemDict, None, None)
        self.mySystemResources.setMyMode(self.mode)
        self.myWidgets.append(self.mySystemResources)
    
    def createGalaxyPrices(self):
        self.myGalaxyPrices = systemresources.GalaxyResourcePrices(self.path, self.posInitX+0.05, self.posInitY+0.45, 
                                                                 self.mySystemDict, None, None)
        self.myGalaxyPrices.setMyMode(self.mode)
        self.myGalaxyPrices.createGalaxyResourcePrices()
        self.myWidgets.append(self.myGalaxyPrices)
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['buyia','buyec','buyal']:
            buttonPosition = (self.posInitX,0,self.posInitY+y*0.0525)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
            
        y = -1
        for key in ['selectall','sellia','sellec','sellal']:
            buttonPosition = (self.posInitX+0.55,0,self.posInitY+y*0.0525)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
    
    def disableMarketButtons(self):
        """Decide which buttons should be disabled"""
        system = self.mode.systemmenu.mySystemDict
        if system['cities'] < 40:
            for key in ['buyia','buyec','buyal']:
                self.disableButton(key)
            self.createTitleCard('disable1','Only Capital Systems of 40+ can place Buy Orders',
                                 20,self.posInitX-0.25,self.posInitY-0.0525)
        self.disableButton('selectall')
        for res in ['AL','EC','IA']:
            if system[res] == 0:
                self.disableButton('sell%s' % string.lower(res))
            else:
                self.enableButton('selectall')
            
    def presssellal(self):
        """Sell AL"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketSellGui('AL')
    
    def presssellec(self):
        """Sell EC"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketSellGui('EC')
    
    def presssellia(self):
        """Sell IA"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketSellGui('IA')
    
    def pressselectall(self):
        """Sell All resources"""
        system = self.mode.systemmenu.mySystemDict
        for res in ['AL','EC','IA']:
            price = self.mode.game.prices[res]
            if system[res] > 0:
                order = {'type':'sell', 'value':res, 'min':price, 'max':0.0, 'amount':system[res], 'system':system['id']}
                self.mode.submitMarketOrder(order)
        
    def pressbuyal(self):
        """Buy AL"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketBuyGui('AL')
    
    def pressbuyec(self):
        """Buy EC"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketBuyGui('EC')
    
    def pressbuyia(self):
        """Buy IA"""
        self.mode.systemmenu.press4()
        self.mode.systemmenu.createSystemMarketBuyGui('IA')
    
if __name__ == "__main__":
    myMenu = SystemMarketMenu('media')
    run()