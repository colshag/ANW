# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# textentry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allow user to enter text using keyboard, disable shortcut keys
# ---------------------------------------------------------------------------
from direct.gui.DirectGui import DirectEntry
from anw.func import globals
from anw.gui import textonscreen
        
class TextEntry(object):
    """Enter Text using Keyboard, disable shortcut keys"""
    def __init__(self, path, mode, command, initialText='', title='Title', 
                 lines=1, width=20, x=0, z=0, font=5, titleWidth=30, textDelta=0.055):
        self.titleWidth = titleWidth
        self.textDelta = textDelta
        self.path = path
        self.mode = mode
        self.command = command
        self.initial=initialText
        self.title = title
        self.lines = lines
        self.width = width
        self.myEntry = None
        self.myTitle = None
        self.x = x
        self.z = z
        self.y = 0
        self.scale = 0.03
        self.font = '%s/star%s' % (self.path, font)
        self.myFont = loader.loadFont(self.font)
        self.setMyEntry()
        self.createTitleCard()
    
    def createTitleCard(self):
        """Default Title label"""
        self.myTitle = textonscreen.TextOnScreen(self.path, self.title, 0.025, 5, aspect2d)
        self.myTitle.writeTextToScreen(self.x+0.01, 0, self.z+self.textDelta, self.titleWidth)
        self.myTitle.setTitleStyle()
        
    def setMyEntry(self):
        self.myEntry = DirectEntry(text='', scale=self.scale, command=self.onCommand,
                                   numLines=self.lines, width=self.width,
                                   pos=(self.x,self.y,self.z),entryFont=self.myFont,
                                   focusInCommand=self.onFocus, focusOutCommand=self.onOutFocus,
                                   frameColor=(0,0,0,.7), text_fg=(1,1,1,1), initialText=self.initial, 
                                   clickSound=self.mode.game.app.beep01Sound,
                                   rolloverSound=None)
    
    def onCommand(self, textEntered):
        self.setShortcuts()
        myMethod = getattr(self.mode, self.command)
        myMethod(textEntered)
        
    def destroy(self):
        self.myEntry.destroy()
        self.myTitle.destroy()
    
    def onFocus(self):
        self.ignoreShortcuts()
        self.mode.onEntryFocus()
    
    def onOutFocus(self):
        self.mode.setShortcuts()
        self.mode.onEntryOutFocus()
    
    def ignoreShortcuts(self):
        """Ignore all keyboard shortcuts created"""
        self.mode.game.app.ignoreAll()
        
    def setShortcuts(self):
        self.mode.setShortcuts()
    
    