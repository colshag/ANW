# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# scrollvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to create a number
# number is saved to mode, number can be negative
# ---------------------------------------------------------------------------
import string

import direct.directbase.DirectStart
from pandac.PandaModules import TextNode
from rootbutton import RootButton
from anw.func import globals, funcs
from anw.gui import textonscreen

class ScrollValue(RootButton):
    """The Scroll Value Gui"""
    def __init__(self, path, x, y, name, default='X'):
        RootButton.__init__(self, path, x, y, name)
        self.allKeys = ['A','S','D','Z','X','C']
        self.myText = None
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C']
        self.id = ''
        self.font = loader.loadFont('%s/star5' % self.path)
        self.currentValue = 0
        self.maxValue = 0
        self.minValue = 0
        self.createTextCard()
        self.pressButton(default)
        if hasattr(self, 'button_S'):
            self.disableButton('S')
        self.createTitleCard('scrollTitle1','Choose Amount of Research to Add or Subtract:',
                         12,self.posInitX-0.04,self.posInitY+0.316)
    
    def setID(self, id):
        self.id = id
    
    def setMaxValue(self, value):
        self.maxValue = value
    
    def setMinValue(self, value):
        self.minValue = value
    
    def createTextCard(self):
        """Text Card stored current Scroll Value"""
        self.myText = TextNode('scrollValue')
        self.setCurrentValue(0)
        self.myText.setFont(self.font)
        self.myText.setCardColor(globals.colors['guiblue3'])
        self.myText.setFrameColor(globals.colors['guiblue2'])
        self.myText.setFrameAsMargin(0, 0, 0, 0)
        self.myText.setFrameLineWidth(3)
        self.myText.setCardAsMargin(.1, .1, .1, .1)
        textNodePath = aspect2d.attachNewNode(self.myText)
        textNodePath.setScale(0.09)
        textNodePath.setPos(self.posInitX-0.04, 0, self.posInitY+0.175)
        self.myWidgets.append(textNodePath)
    
    def setCurrentValue(self, value):
        """Set the current Value to be displayed"""
        if self.validateValue(value):
            self.currentValue = value
            value = str(value)
            if len(value) == 1:
                value = '0' + value
            self.myText.setText(' %s' % value)
            self.setTextColor()
            self.enableSubmit()
    
    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.currentValue == 0:
            self.disableButton('S')
        else:
            self.enableButton('S')
    
    def validateValue(self, value):
        """Validate that value can be set"""
        if value > self.maxValue:
            return 0
        if value < self.minValue:
            return 0
        return 1
    
    def setTextColor(self):
        """Make text Green if positive, red if negative"""
        if self.currentValue < 0:
            self.myText.setTextColor(globals.colors['guired'])
        elif self.currentValue > 0:
            self.myText.setTextColor(globals.colors['guigreen'])
        else:
            self.myText.setTextColor(globals.colors['guiblue1'])
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        for key in ['Z','X','C']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
        self.x = 0
        self.y = 1
        for key in ['A','S','D']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
                
    def pressS(self):
        """Submit value to server"""
        self.mode.addTechOrder(self.currentValue, self.id)
        self.disableButton('S')
    
    def pressD(self):
        """Increment Value"""
        self.setCurrentValue(self.currentValue + self.scrollFactor)
    
    def pressA(self):
        """Decrement Value"""
        self.setCurrentValue(self.currentValue - self.scrollFactor)
   
    def pressZ(self):
        """Set scroll factor to 1"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.scrollFactor = 1        
    
    def pressX(self):
        """Set scroll factor to 5"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.scrollFactor = 5
    
    def pressC(self):
        """Set scroll factor to 10"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.scrollFactor = 10

if __name__ == "__main__":
    myScrollValue = ScrollValue('media', -0.3, -0.17, 'scroll')
    myScrollValue.setMaxValue(219)
    myScrollValue.setMinValue(-119)
    run()