# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# tradevalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to modify the
# trade routes between systems
# ---------------------------------------------------------------------------
import copy

from rootbutton import RootButton
from anw.gui import valuebar, textonscreen
from anw.func import globals

class TradeValue(RootButton):
    """The Trade Value Gui"""
    def __init__(self, path, mySystemDict, toSystemDict, myTradeRouteDict, x=-1.24, y=-0.35):
        self.mySystemDict = mySystemDict
        self.toSystemDict = toSystemDict
        self.myTradeRouteDict = myTradeRouteDict
        RootButton.__init__(self, path, x=x, y=y, name='trade')
        self.allKeys = ['A','S','D','Z','X','C','V','F','G']
        self.scale = 0.25
        self.tradeBars = None
        self.textTradeDescription = None
        self.writeTradeDescription()
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C', 'G', 'F', 'V']
        self.resource = 0 # 0=AL,1=EC,2=IA
        self.scrollFactor = 0
        self.pressButton('C')
        self.pressButton('G')
        self.disableSubmitButtons()
        self.disableButton('cancel')
        self.createDefaultTradeRoute()
        self.maxResourceAmounts = [self.myTradeRouteDict['AL']+self.mySystemDict['AL'], 
                                   self.myTradeRouteDict['EC']+self.mySystemDict['EC'],
                                   self.myTradeRouteDict['IA']+self.mySystemDict['IA']]

        self.tradeResourceAmounts = [self.myTradeRouteDict['AL'], self.myTradeRouteDict['EC'],
                                     self.myTradeRouteDict['IA']]
        self.initTradeResourceAmounts = copy.copy(self.tradeResourceAmounts)
        self.createTradeBars()
    
    def createDefaultTradeRoute(self):
        """Create the default trade route if required"""
        if self.myTradeRouteDict == None:
            d = {}
            d['fromSystem'] = self.mySystemDict['id']
            d['toSystem'] = self.toSystemDict['id']
            d['type'] = 'REG'
            d['AL'] = 0
            d['EC'] = 0
            d['IA'] = 0
            d['oneTime'] = 0
            self.myTradeRouteDict = d

    def setTradeRouteID(self):
        if 'id' not in self.myTradeRouteDict.keys():
            self.myTradeRouteDict['id'] = '%s-%s-%s' % (self.myTradeRouteDict['fromSystem'], 
                                                        self.myTradeRouteDict['toSystem'], 
                                                        self.myTradeRouteDict['type'])

    def writeTradeDescription(self):
        """Create Trade Description"""
        text = 'Trade From:\n\n %s \n\n\nTrade To:\n\n %s ' % (self.mySystemDict['name'], self.toSystemDict['name'])
        if self.textTradeDescription == None:
            self.textTradeDescription = textonscreen.TextOnScreen(self.path, text,
                                                          scale=0.020, font=5, parent=aspect2d)
            self.textTradeDescription.writeTextToScreen(self.posInitX+0.25, 0, self.posInitY+0.216, 10)
            self.textTradeDescription.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 1, 1)
            self.textTradeDescription.setColor(globals.colors['guiyellow'])
            self.myWidgets.append(self.textTradeDescription)
        else:
            self.textTradeDescription.myText.setText(text)
            
    def setResource(self, resource):
        self.resource = resource
    
    def createTradeBars(self):
        """Trade Route Resource Breakdown:"""
        x = self.posInitX
        y = self.posInitY+0.350
        self.createTitleCard('tradeTitle1','Modify or Cancel Trade Route:',
                         30,x-0.04, y+0.042)
        self.tradeBars = valuebar.IndustryBars(self.path, self.tradeResourceAmounts,
                                                      self.maxResourceAmounts,x=x+0.20,
                                                      y=y,scale=self.scale)
        self.myWidgets.append(self.tradeBars)
    
    def setResourceValue(self, value):
        """Update tradeBars based on resource currently being changed"""
        validValue = self.getValidValue(value)
        self.tradeResourceAmounts[self.resource] = validValue
        self.tradeBars.updateValueBars(self.tradeResourceAmounts)
        self.setMyTradeRouteDict()
        self.enableSubmit()
    
    def setMyTradeRouteDict(self):
        self.myTradeRouteDict['AL'] = self.tradeResourceAmounts[0]
        self.myTradeRouteDict['EC'] = self.tradeResourceAmounts[1]
        self.myTradeRouteDict['IA'] = self.tradeResourceAmounts[2]
    
    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.tradeResourceAmounts != self.initTradeResourceAmounts and self.tradeResourceAmounts != [0,0,0]:
            self.enableSubmitButtons()
        else:
            self.disableSubmitButtons()

    def enableSubmitButtons(self):
        self.enableButton('S')
        self.enableButton('onetime')
    
    def disableSubmitButtons(self):
        self.disableButton('S')
        self.disableButton('onetime')
    
    def getValidValue(self, value):
        """if value being submitted is too big or too small for max
        or min value then set value to max or min value"""
        newValue = self.tradeResourceAmounts[self.resource] + value
        maxValue = self.maxResourceAmounts[self.resource]
        if value > 0:#trying to add
            if newValue > maxValue:
                return maxValue
            else:
                return newValue
        else:# trying to remove
            if newValue < 0:
                return 0
            else:
                return newValue
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        x = 5
        y = 1
        for key in ['V','F','G']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            y += 1
        x = 0
        y = 1
        for key in ['Z','X','C']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        x = 0
        y = 2
        for key in ['A','S','D']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        y = 0
        for key in ['onetime','tradegen','cancel']:
            buttonPosition = (self.posInitX+0.2,0,(self.posInitY+0.03+y*.09))
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.045)
            y -= 0.5

    def presscancel(self):
        """Submit to Server"""
        self.disableSubmitButtons()
        self.mode.cancelTradeRoute(self.myTradeRouteDict['id'])

    def pressonetime(self):
        """Submit to Server"""
        self.disableSubmitButtons()
        self.myTradeRouteDict['oneTime'] = 1
        self.setTradeRouteID()
        self.mode.addTradeRoute(self.myTradeRouteDict)
    
    def presstradegen(self):
        """Submit to Server"""
        self.disableSubmitButtons()
        self.myTradeRouteDict['type'] = 'GEN'
        self.setTradeRouteID()
        self.mode.addTradeRoute(self.myTradeRouteDict)
            
    def pressS(self):
        """Submit value to server"""
        self.setTradeRouteID()
        self.disableSubmitButtons()
        self.mode.addTradeRoute(self.myTradeRouteDict)
    
    def pressD(self):
        """Increment Value"""
        self.setResourceValue(self.scrollFactor)
    
    def pressA(self):
        """Decrement Value"""
        self.setResourceValue(-self.scrollFactor)
   
    def pressZ(self):
        """Set scroll factor to 5"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.scrollFactor = 5        
    
    def pressX(self):
        """Set scroll factor to 100"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.scrollFactor = 100
    
    def pressC(self):
        """Set scroll factor to 1000"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.scrollFactor = 1000
    
    def pressG(self):
        """Set resource to AL"""
        self.enableLastButton2('G')
        self.disableButton('G')
        self.setResource(0)
    
    def pressF(self):
        """Set resource to EC"""
        self.enableLastButton2('F')
        self.disableButton('F')
        self.setResource(1)
    
    def pressV(self):
        """Set resource to IA"""
        self.enableLastButton2('V')
        self.disableButton('V')
        self.setResource(2)
    
if __name__ == "__main__":
    systemDict = {'id':'1','AL':1200, 'EC':110, 'IA':330, 'name':'SystemName1'}
    toSystemDict = {'id':'3', 'name':'SystemName2'}
    myTradeValue = TradeValue('media', systemDict, toSystemDict, myTradeRouteDict=None)
    run()