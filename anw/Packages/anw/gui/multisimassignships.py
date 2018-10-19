# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# multisimassignships.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows a number of ships to be assigned to either Team 1 or Team 2
# for a multi ship design battle.
# ---------------------------------------------------------------------------
import copy

from rootbutton import RootButton
from anw.gui import valuebar, textonscreen
from anw.func import globals

class MultiSimAssignShips(RootButton):
    """Choose number of ships and which team to assign the design to"""
    def __init__(self, path, designName, maxNum, shipDesignID, x=0.5, y=-0.8):
        self.designName = designName
        self.shipDesignID = shipDesignID
        RootButton.__init__(self, path, x=x, y=y, name='multisim')
        self.allKeys = ['A','S','D','Z','X']
        self.scale = 0.25
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X']
        self.scrollFactor = 1
        self.maxValue = maxNum
        self.selected = 1 #team 1, team 2
        self.shipNum = None
        self.shipCount = 1
        self.pressButton('Z')
        self.enableSubmitButtons()
        
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
        self.createTitleCard('title','Choose number of %s to add to Team 1 or 2:' % self.designName,
                         15,x-0.04, y+0.085)
        self.shipNum = valuebar.ValueBar(self.path, scale=self.scale,
                                      extraText = ' SHIPS TO ADD')
        self.shipNum.setColor(globals.colors['guiwhite'])
        self.shipNum.setMyValues(1, self.maxValue)
        self.shipNum.setMyPosition(x+0.20, 0, y-0.02)
        self.myWidgets.append(self.shipNum)
    
    def setSelectedValue(self, value):
        """Update Selected Value"""
        if self.validateValue(value):
            self.shipCount += value
            self.shipNum.setMyValues(self.shipCount, self.maxValue)
            self.enableSubmit()

    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        self.enableSubmitButtons()
            
    def enableSubmitButtons(self):
        self.enableButton('S')
    
    def disableSubmitButtons(self):
        self.disableButton('S')
    
    def validateValue(self, value):
        """Validate value can be added or removed"""
        newValue =  self.shipCount + value
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
        x = 0
        y = 1
        for key in ['Z','X']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+0.059+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        x = 0
        y = 2
        for key in ['A','S','D']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY+0.059+y*.10))
            self.createButton(key, buttonPosition)
            x += 1
        
    def pressS(self):
        """Submit value to server"""
        self.disableSubmitButtons()
        d = self.mode.multisim[self.selected]
        if self.shipDesignID not in d.keys():
            d[self.shipDesignID] = self.shipCount
        else:
            d[self.shipDesignID] += self.shipCount
        self.mode.refreshMultiSim()
    
    def pressD(self):
        """Increment Value"""
        self.setSelectedValue(self.scrollFactor)
    
    def pressA(self):
        """Decrement Value"""
        self.setSelectedValue(-self.scrollFactor)
   
    def pressZ(self):
        """Assign Ship Design to Team 1"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.selected = 1        
    
    def pressX(self):
        """Assign Ship Design to Team 2"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.selected = 2
    
if __name__ == "__main__":
    myMultiGUI = MultiSimAssignShips('media','HEAVY CARRIER',20, '1')
    myMultiGUI.setMyMode(None)
    run()