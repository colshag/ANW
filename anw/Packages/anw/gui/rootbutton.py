# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# rootbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the root parent gui object that contains keyboard shortcut standard
# buttons.  It can be extended as required
# ---------------------------------------------------------------------------
import string

from pandac.PandaModules import TextNode
from direct.task import Task
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectButton
from anw.func import globals

class RootButton(DirectObject):
    """The Scroll Value Gui"""
    def __init__(self, path, x, y, name, ignoreShortcutButtons = []):
        self.game = None
        self.mode = None
        self.color = ''
        self.name = name
        self.path = path
        self.font = loader.loadFont('%s/star5' % self.path)
        self.posInitX = x
        self.posInitY = y
        self.x = 0
        self.y = 0
        self.myWidgets = []
        self.visable = 1
        self.disableButtonTime = 1.0
        self.disableButtonIgnore = []
        self.disabledButtons = []
        self.ignoreShortcutButtons = ignoreShortcutButtons
        self.allKeys = [] # fill this in to allow for renabling key shortcuts
        self.lastKey = ''
        self.lastKey2 = '' # in case you want to sets of disable groups
        if name != '':
            self.createButtons()
        self.acceptExtraKeys()
    
    def setPause(self):
        """Allow mode to pause using space bar"""
        self.accept('space', self.mode.pauseResume)
    
    def setMyColor(self):
        """Set the color using empire color1 from game"""
        self.color = globals.empires[int(self.game.myEmpireID)]['color1']
        self.color = globals.colors[self.color]
    
    def setMyGame(self, game):
        """Set the game object"""
        self.game = game

    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode
        self.disableZoom()
    
    def acceptExtraKeys(self):
        """Accept extra keyboard or mouse commands to object methods"""
        pass
    
    def acceptSpaceBarKey(self):
        self.accept("space", self.mode.onSpaceBarClear)
        self.accept("escape", self.mode.onSpaceBarClear)
        
    def createTitleCard(self, name, text, wordwrap, x, z, scale=0.025):
        """Default Title label for gui controls"""
        self.myTitle = TextNode(name)
        self.myTitle.setFont(self.font)
        self.myTitle.setText(text)
        self.myTitle.setWordwrap(wordwrap)
        self.myTitle.setTextColor(globals.colors['guiwhite'])
        self.myTitle.setCardColor(globals.colors['guiblue3'])
        self.myTitle.setFrameColor(globals.colors['guiblue2'])
        self.myTitle.setFrameAsMargin(.3, .5, .5, .5)
        self.myTitle.setFrameLineWidth(3)
        self.myTitle.setCardAsMargin(.3, .5, .5, .5)
        textNodePath = aspect2d.attachNewNode(self.myTitle)
        textNodePath.setScale(scale)
        textNodePath.setPos(x, 0, z)
        self.myWidgets.append(textNodePath)
    
    def createButtons(self):
        """Create all Buttons"""
        for key in ['Z','X','C']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
    
    def createButton(self, key, buttonPosition, geomX=0.10, geomY=0.10):
        """Create Button based on buttonKey, and position given"""
        maps = loader.loadModel('%s/%s_%s_maps.egg' % (self.path, self.name, key))
        myButton = DirectButton(geom = (maps.find('**/%s_%s_ready' % (self.name, key)),
                                        maps.find('**/%s_%s_click' % (self.name, key)),
                                        maps.find('**/%s_%s_rollover' % (self.name, key)),
                                        maps.find('**/%s_%s_disabled' % (self.name, key))),
                                borderWidth = (0,0),
                                geom_scale = (geomX,1,geomY),
                                pressEffect = 0,
                                command = self.pressButton,
                                extraArgs = [key],
                                pos = buttonPosition,
                                rolloverSound = None,
                                clickSound = None)
        
        setattr(self, 'button_%s' % key, myButton)
        self.setAcceptOnButton(key)
        self.myWidgets.append(myButton)
        
    def pressR(self):
        """Set resource to AL"""
        self.enableFactorButtons()
        self.disableButton('R')
        self.setResource(1)
    
    def pressF(self):
        """Set resource to EC"""
        self.enableFactorButtons()
        self.disableButton('F')
        self.setResource(2)
    
    def pressV(self):
        """Set resource to IA"""
        self.enableFactorButtons()
        self.disableButton('V')
        self.setResource(3)
    
    def setAcceptOnButton(self, key):
        """Map button to key"""
        if key not in self.ignoreShortcutButtons:
            self.accept(string.lower(key), self.pressButton, [key])
    
    def destroy(self):
        """Destroy gui"""
        self.removeMyWidgets()
    
    def removeMyWidgets(self):
        """Remove all sub widgets"""
        for myWidget in self.myWidgets:
            self.removeMyWidget(myWidget)
        self.ignoreAll()
    
    def removeMyWidget(self, myWidget):
        """Remove one widget"""
        if myWidget != None:
            try:
                myWidget.removeNode()
            except:
                myWidget.destroy()               

    def enableZoom(self):
        if self.mode:
            self.mode.enableScrollWheelZoom = 1

    def disableZoom(self):
        if self.mode:
            self.mode.enableScrollWheelZoom = 0
        
    def hideAll(self):
        """Hide all the buttons"""
        for myWidget in self.myWidgets:
            myWidget.hide()
        self.visable = 0
    
    def showAll(self):
        """Show all the buttons"""
        for myWidget in self.myWidgets:
            myWidget.show()
        self.visable = 1
    
    def pressButton(self, key):
        """Called when button is pressed or shortcut key is pressed"""
        #self.mode.stopCameraTasks()
        taskMgr.remove('zoomInCameraTask')
        taskMgr.remove('zoomOutCameraTask')
        if key not in self.disabledButtons or key not in self.disableButtonIgnore:
            myMethod = getattr(self, 'press' + key)
            myMethod()
            self.checkDisableButton(key)
            if self.mode != None:
                self.mode.playSound('beep01')
        
    
    def checkDisableButton(self, key):
        """Should button be disabled after execution?  Look at disableButtonTime
        -1 : don't disable button
        0 : disable button and no task to re-enable
        x : disable button and set task to re-enable after x seconds"""
        if self.disableButtonTime == -1 or key in self.disableButtonIgnore:
            return
        elif self.disableButtonTime == 0:
            self.disableButton(key)
        else:
            self.disableButton(key)
            taskMgr.doMethodLater(self.disableButtonTime, self.enableButton, 'enableButtonTask', extraArgs = [key])
        
    def disableButton(self, key):
        """disable the button"""
        myButton = getattr(self, 'button_%s' % key)
        myButton.guiItem.setActive(0)
        if key not in self.disabledButtons:
            self.disabledButtons.append(key)
    
    def enableButton(self, key):
        """enable the button"""
        myButton = getattr(self, 'button_%s' % key)
        myButton.guiItem.setActive(1)
        if key in self.disabledButtons:
            self.disabledButtons.remove(key)
    
    def enableLastButton(self, key):
        """enable the last button pressed"""
        if self.lastKey != '':
            self.enableButton(self.lastKey)
        self.lastKey = key
    
    def enableLastButton2(self, key):
        """enable the last button pressed from group 2"""
        if self.lastKey2 != '':
            self.enableButton(self.lastKey2)
        self.lastKey2 = key
    
    def toggleButtons(self):
        """Hide or Show the buttons"""
        if self.visable == 1:
            self.hideAll()
        else:
            self.showAll()
    
    def enterMode(self, myMode):
        """Enter the new mode"""
        self.mode = myMode
        newMode = myMode(self.game)
        self.game.enterMode(newMode)
    
    def ignoreShortcuts(self):
        """Ignore all keyboard shortcuts created"""
        self.ignoreAll()
    
    def setShortcuts(self):
        """Set all keyboard shortcuts"""
        for key in self.allKeys:
            self.setAcceptOnButton(key)
        
