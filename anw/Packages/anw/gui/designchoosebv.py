# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# designchoosebv.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to choose
# Battle Value amount for both designs
# ---------------------------------------------------------------------------
import copy

from rootbutton import RootButton
from anw.gui import valuebar, textonscreen
from anw.func import globals

class DesignChooseBV(RootButton):
    """The Design Choose Battle Value Gui"""
    def __init__(self, path, otherDesignID, x=0.5, y=-0.8):
        self.otherDesignID = otherDesignID
        RootButton.__init__(self, path, x=x, y=y, name='bv')
        self.allKeys = ['A','S','D','Z','X','C','V','F']
        self.scale = 0.25
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C', 'F', 'V']
        self.scrollFactor = 0
        self.maxValue = 50.0
        self.selected = 0 #mine=0, other=1
        self.pressButton('X')
        self.pressButton('F')
        self.enableSubmitButtons()
        self.myBV = None
        self.otherBV = None
        self.myValues = [10.0,10.0]
        
    def setSelected(self, selected):
        self.selected = selected
    
    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode
        self.createValueBars()
        
    def createValueBars(self):
        """Create Value Bars:"""
        x = self.posInitX
        y = self.posInitY+0.350
        name = self.mode.game.shipDesignObjects[self.otherDesignID].name
        self.createTitleCard('bvTitle1','Choose Ship Numbers for Simulation:',
                         30,x-0.04, y+0.042)
        self.myBV = valuebar.ValueBar(self.path, scale=self.scale,
                                      extraText = ' OF MY DESIGN')
        self.myBV.setColor(globals.colors['guiwhite'])
        self.myBV.setMyValues(self.myValues[0], self.maxValue)
        self.myBV.setMyPosition(x+0.20, 0, y-0.02)
        self.myWidgets.append(self.myBV)
        barHeight = self.myBV.myBar.getHeight()*self.scale
        self.otherBV = valuebar.ValueBar(self.path, scale=self.scale,
                                      extraText = ' OF OTHER DESIGN')
        self.otherBV.setColor(globals.colors['guigrey'])
        self.otherBV.setMyValues(self.myValues[0], self.maxValue)
        self.otherBV.setMyPosition(x+0.20, 0, y-barHeight-0.02)
        self.myWidgets.append(self.otherBV)
    
    def setSelectedValue(self, value):
        """Update Selected Value"""
        if self.validateValue(value):
            self.myValues[self.selected] += value
            if self.selected == 0:
                self.myBV.setMyValues(self.myValues[self.selected], self.maxValue)
            else:
                self.otherBV.setMyValues(self.myValues[self.selected], self.maxValue)
            self.enableSubmit()

    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.myValues[0] > 0 and self.myValues[1] > 0:
            self.enableSubmitButtons()
        else:
            self.disableSubmitButtons()
            
    def enableSubmitButtons(self):
        self.enableButton('S')
    
    def disableSubmitButtons(self):
        self.disableButton('S')
    
    def validateValue(self, value):
        """Validate value can be added or removed"""
        newValue =  self.myValues[self.selected] + value
        maxValue = self.maxValue
        if value > 0:#trying to add
            if newValue > maxValue:
                return 0
            else:
                return 1
        else:# trying to remove
            if newValue < maxValue and newValue >= 0:
                return 1
            else:
                return 0
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        x = 5
        y = 2
        for key in ['V','F']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition)
            y += 1
        x = 0
        y = 1
        for key in ['Z','X','C']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+0.02+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        x = 0
        y = 2
        for key in ['A','S','D']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+0.02+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        y = 0
        
    def pressS(self):
        """Submit value to server"""
        self.disableSubmitButtons()
        self.mode.selectedShipHull.myBV = self.myValues[0]
        self.mode.selectedShipHull.otherBV = self.myValues[1]
        self.mode.selectedShipHull.simulateMyDesign(self.otherDesignID)
    
    def pressD(self):
        """Increment Value"""
        self.setSelectedValue(self.scrollFactor)
    
    def pressA(self):
        """Decrement Value"""
        self.setSelectedValue(-self.scrollFactor)
   
    def pressZ(self):
        """Set scroll factor to 1"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.scrollFactor = 1        
    
    def pressX(self):
        """Set scroll factor to 10"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.scrollFactor = 5
    
    def pressC(self):
        """Set scroll factor to 100"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.scrollFactor = 10
    
    def pressF(self):
        """Set value"""
        self.enableLastButton2('F')
        self.disableButton('F')
        self.setSelected(0)
    
    def pressV(self):
        """Set value"""
        self.enableLastButton2('V')
        self.disableButton('V')
        self.setSelected(1)
    
if __name__ == "__main__":
    myLeverage = DesignChooseBV('media')
    run()