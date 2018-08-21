# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# questionsurrender.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# As the player if they want to end the round
# ---------------------------------------------------------------------------
import string
from anw.func import globals, funcs
from anw.gui import scrollvalue, rootbutton

class QuestionSurrender(rootbutton.RootButton):
    """Ask the player if they want to Surrender"""
    def __init__(self, path, x=-0.5, y=0):
        self.posInitX = x
        self.posInitY = y
        self.industrySim = None
        self.textTitle = None
        self.textDescription = None
        rootbutton.RootButton.__init__(self, path, x=x, y=y, name='questionsurrender')
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['blankyes','blankno']:
            buttonPosition = (self.posInitX+y*0.925,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
        
    def pressblankyes(self):
        self.mode.surrender()
    
    def pressblankno(self):
        self.mode.clearMyGui()
        self.mode.modeMsgBox('Good for you! Never Give Up!')
            
if __name__ == "__main__":
    myGui = QuestionSurrender('media')
    run()
    
    