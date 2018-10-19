# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# textonscreen.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays Text in the game in a consistant manner
# ---------------------------------------------------------------------------
from pandac.PandaModules import TextNode
from direct.task import Task
from anw.func import globals
        
class TextOnScreen(object):
    """Display Text on the screen"""
    def __init__(self, path, text, scale, font=5, parent=render):
        self.path = path
        self.text = text
        self.parent = parent
        self.fadeCount = 100.0
        self.fadeAmount = 0.0
        self.x = 0
        self.z = 0
        self.y = 0
        self.text = text
        self.scale = scale
        self.font = '%s/star%s' % (self.path, font)
        self.myText = None
        self.textNodePath = None
    
    def setMyPosition(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        if self.textNodePath:
            self.textNodePath.setPos(x, y, z)
    
    def writeTextToScreen(self, x, y, z, wordwrap=10):
        """Write the text"""
        self.myText = TextNode(self.text)
        self.myText.setText(self.text)
        myFont = loader.loadFont(self.font)
        self.myText.setFont(myFont)
        self.myText.setWordwrap(wordwrap)
        self.textNodePath = self.parent.attachNewNode(self.myText)
        self.textNodePath.setScale(self.scale)
        #self.textNodePath.setBillboardPointEye()
        self.setMyPosition(x, y, z)
        self.textNodePath.setTransparency(1)
    
    def setCardColor(self, color, left=0.3, right=0.5, down=0.5, up=0.5):
        self.myText.setCardColor(color)
        self.myText.setCardAsMargin(left, right, down, up)
    
    def setFrameColor(self, color, left=0.3, right=0.5, down=0.5, up=0.5):
        self.myText.setFrameColor(color)
        self.myText.setFrameAsMargin(left, right, down, up)
    
    def setColor(self, color):
        """set the text color = Vec4(red, green, blue, alpha)"""
        self.textNodePath.setColor(color)
       
    def destroy(self):
        """remove text"""
        self.textNodePath.removeNode()
    
    def setTitleStyle(self):
        self.setCardColor(globals.colors['guiblue3'])
        self.setFrameColor(globals.colors['guiblue2'])
        self.myText.setTextColor(globals.colors['guiwhite'])
        self.myText.setFrameLineWidth(3)
    
    def startFade(self, amount=2.0):
        self.fadeAmount = amount
        taskMgr.add(self.fadeText, 'fadeTextTask')
    
    def fadeText(self, task):
        """Fade out the text and destroy"""
        if self.fadeCount <= 0:
            self.destroy()
            return Task.done
        else:
            self.fadeCount -= self.fadeAmount
            self.textNodePath.setAlphaScale(self.fadeCount/100.0)
            return Task.cont

    