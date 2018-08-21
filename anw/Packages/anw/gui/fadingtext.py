# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# fadingtext.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays Text in the game that fades and stays in aspect2d
# ---------------------------------------------------------------------------
from pandac.PandaModules import TextNode, Vec3
from direct.task import Task

from anw.func import globals
        
class FadingText(object):
    """Display Text on the screen"""
    def __init__(self, path, text, messagePositions):
        self.path = path
        self.text = text
        self.fadeCount = 100.0
        self.messagePositions = messagePositions
        self.x = 0
        self.y = 0
        self.text = text
        self.scale = 0.04
        self.font = '%s/star5' % self.path
        self.myText = None
        self.textNodePath = None
        self.setMyPosition()
        self.createMessage()
    
    def getMyPosition(self):
        return self.y
    
    def setMyPosition(self):
        """Move message where other current messages are not"""
        self.x = -0.7
        for i in range(20):
            num = -0.97 + (0.10 * i)
            if num not in self.messagePositions:
                self.y = num
                return
    
    def createMessage(self):
        """Write the text"""
        self.myText = TextNode(self.text)
        self.myText.setText(self.text)
        myFont = loader.loadFont(self.font)
        self.myText.setFont(myFont)
        self.myText.setWordwrap(40)
        self.textNodePath = aspect2d.attachNewNode(self.myText)
        self.textNodePath.setScale(self.scale)
        self.textNodePath.setPos(Vec3(self.x, 0, self.y))
        self.textNodePath.setTransparency(1)
        self.textNodePath.setColor(globals.colors['guiyellow'])
        taskMgr.add(self.fadeMessage, 'fadeMessageTask')
    
    def removeMessage(self):
        """Remove the current Message"""
        self.textNodePath.removeNode()
        self.messagePositions.remove(self.y)
    
    def fadeMessage(self, task):
        """Fade the current Message"""
        if self.fadeCount <= 0:
            self.removeMessage()
            return Task.done
        else:
            self.fadeCount -= 0.3
            self.textNodePath.setAlphaScale(self.fadeCount/100.0)
            return Task.cont

    