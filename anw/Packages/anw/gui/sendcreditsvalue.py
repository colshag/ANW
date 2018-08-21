# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sendcreditsvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to 
# send credits to another empire
# ---------------------------------------------------------------------------
from rootbutton import RootButton
from anw.gui import valuebar, textonscreen
from anw.func import globals

class SendCreditsValue(RootButton):
    """SEnd Credits to another empire"""
    def __init__(self, path, empireDict, systemID, toName):
        self.empireDict = empireDict
        self.systemID = systemID
        y = -0.15
        x = -0.95
        RootButton.__init__(self, path, x=x, y=y, name='sendcredit')
        self.allKeys = ['A','S','D','Z','X','C','V']
        self.scale = 0.25
        self.amountBar = None
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S','Z','X','C','V']
        self.currentAmount = 0.0
        self.scrollFactor = 0
        self.pressButton('V')
        self.createTitleCard('marketTitle','Select Credits to send to %s:' % toName,
                         30,x-0.04, y+0.315)
        self.createAmountBar()
    
    def createAmountBar(self):
        """choose amount to send"""
        self.amountBar = valuebar.ValueBar(self.path, scale=self.scale, extraText = ' CREDITS', showOverValues=0)
        self.amountBar.setMyValues(100.0, self.empireDict['CR'])
        barHeight = self.amountBar.myBar.getHeight()*self.scale
        self.amountBar.setMyPosition(self.posInitX+0.20, 0, self.posInitY+0.31-barHeight)
        color = globals.resourceColors['CR']
        self.amountBar.setColor(globals.colors[color])
        self.myWidgets.append(self.amountBar)
    
    def setValue(self, value):
        """Update Amount Bar by value"""
        validValue = self.getValidValue(value, self.currentAmount, self.empireDict['CR'])
        self.amountBar.setMyValues(validValue, self.empireDict['CR'])
        self.currentAmount = validValue
        color = globals.resourceColors['CR']
        self.amountBar.setColor(globals.colors[color])
        if validValue > 0:
            self.enableButton('S')
        else:
            self.disableButton('S')
    
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
        x = 0
        y = 1
        for key in ['Z','X','C','V']:
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
            
    def pressS(self):
        """Submit value to server"""
        self.mode.submitSendCredits(self.currentAmount)
    
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
        self.scrollFactor = 10
    
    def pressC(self):
        """Set scroll factor to 100"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.scrollFactor = 100
    
    def pressV(self):
        """Set scroll factor to 1000"""
        self.enableLastButton('V')
        self.disableButton('V')
        self.scrollFactor = 1000
        
if __name__ == "__main__":
    empireDict = {'CR':80000}
    myValue = SendCreditsValue('media', empireDict, '1', 'TestEmpire')
    run()
    