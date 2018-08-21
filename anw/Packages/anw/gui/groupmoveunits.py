# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# groupmoveunits.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to move selected
# types of units from one system to another
# ---------------------------------------------------------------------------
import copy

from rootbutton import RootButton
from anw.gui import valuebar

class MoveArmies(RootButton):
    """The Move Armies Gui"""
    def __init__(self, path, x=-1.25, y=0.19, name='movearmies', maxByType=[0,0,0]):
        self.maxByType = maxByType
        self.currentByType = [0,0,0]
        RootButton.__init__(self, path, x=x, y=y, name=name)
        self.allKeys = ['A','S','D','Z','X','C']
        self.scale = 0.29
        self.myBars = None
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C']
        self.type = 0 # 0=Mechanized,1=Artillery,2=Infantry
        self.pressButton('Z')
        self.disableButton('S')
        self.createMoveBars()
    
    def setType(self, type):
        self.type = type
    
    def createMoveBars(self):
        """These bars will show the proposed Marine Type breakdown"""
        x = self.posInitX
        y = self.posInitY + 0.28
        self.createTitleCard('marineTitle1','Select Marine Types to Transit in Bulk:',
                         30,x-0.03, y+0.04)
        self.myBars = valuebar.ColoredBars(self.path, self.currentByType,
                                                      self.maxByType,x=x+0.25,
                                                      y=y,scale=self.scale,
                                                      extraText='Marines', title='',
                                                      identBars = ['Mechanized', 'Artillery', 'Infantry'])
        self.myWidgets.append(self.myBars)
    
    def setValue(self, value):
        """add or remove a value based on type selected already"""
        if self.validateValue(value):
            if value == 1:
                self.currentByType[self.type] += 1
            elif value == -1:
                self.currentByType[self.type] -= 1
            self.myBars.updateValueBars(self.currentByType)
            self.enableSubmit()
    
    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.currentByType != [0,0,0]:
            self.enableButton('S')
        else:
            self.disableButton('S')
    
    def validateValue(self, value):
        """Validate value either adding or removing"""
        if value == 1:
            if self.currentByType[self.type] == self.maxByType[self.type]:
                return 0
            return 1
        elif value == -1:
            if self.currentByType[self.type] == 0:
                return 0
            return 1
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        x = self.posInitX+0.01
        y = self.posInitY+0.01
        for key in ['Z','X','C']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
        self.x = 0
        self.y = 1
        for key in ['A','S','D']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
                
    def pressS(self):
        """Submit value to server"""
        self.mode.populateArmyMove(self.currentByType)
        self.disableButton('S')
    
    def pressD(self):
        """Increment Value"""
        self.setValue(1)
    
    def pressA(self):
        """Decrement Value"""
        self.setValue(-1)
   
    def pressZ(self):
        """Set marineType to Mechanized"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.setType(0)
    
    def pressX(self):
        """Set marineType to Artillery"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.setType(1)
    
    def pressC(self):
        """Set marineType to Infantry"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.setType(2)

class MoveShips(MoveArmies):
    """The Move Ships Gui"""
    def __init__(self, path, x=-1.25, y=0.19, name='movearmada', maxByType=[0,0,0]):
        MoveArmies.__init__(self, path, x, y, name, maxByType)
        self.pressButton('C')
        
    def createMoveBars(self):
        """These bars will show the proposed Ship Type breakdown"""
        x = self.posInitX
        y = self.posInitY + 0.28
        self.createTitleCard('shipTitle1','Select Ship Types to Transit in Bulk:',
                         30,x-0.03, y+0.04)
        self.myBars = valuebar.ColoredBars(self.path, self.currentByType,
                                                      self.maxByType,x=x+0.25,
                                                      y=y,scale=self.scale,
                                                      extraText='', title='',
                                                      identBars = ['Platforms', 'Assault', 'Warships'])
        self.myWidgets.append(self.myBars)
    
    def pressS(self):
        """Submit value to server"""
        self.mode.populateArmadaMove(self.currentByType)
        self.disableButton('S')
        
if __name__ == "__main__":
    #myMoveArmies = MoveArmies('media', -0.3, -0.17, 'movearmies', [10,10,5], 7)
    myMoveShips = MoveShips('media', -0.3, -0.17, 'movearmada', [10,10,5], 7)
    run()