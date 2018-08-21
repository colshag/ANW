# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# questionendround.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# As the player if they want to end the round
# ---------------------------------------------------------------------------
import string

from anw.func import globals, funcs
from anw.gui import scrollvalue, rootbutton
import threading

class QuestionEndRound(rootbutton.RootButton):
    """Ask the player if they want to end the round"""
    def __init__(self, path, x=-0.5, y=0):
        self.posInitX = x
        self.posInitY = y
        self.industrySim = None
        self.textTitle = None
        self.textDescription = None
        rootbutton.RootButton.__init__(self, path, x=x, y=y, name='questionendround')
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['blankyes','blankno','cancel']:
            buttonPosition = (self.posInitX+y*0.525,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
        
    def pressblankyes(self):
        """Player would like to end turn and wait for round to end"""
        self.mode.endAndWait()
    
    def invokeEndRound(self):
        self.mode.game.server.endRound(self.mode.game.authKey)
        
    def pressblankno(self):
        """Player would like to end turn and quit game"""

        # do this action in the background 
        endRoundthread = threading.Thread(target=self.invokeEndRound)
        endRoundthread.daemon = True
        endRoundthread.start()
        # wait up to 5 seconds for that thread to exit... game will then exit..
        endRoundthread.join(5)
        # do not perform a logout! that would cause the thread to lockup again.
        self.mode.exitGame(doLogout=False)
    
    def presscancel(self):
        """Player would not like to cancel"""
        self.mode.game.server.endEmpireTurn(self.mode.game.authKey)
        self.mode.modeMsgBox('You have now un-ended your turn')
        self.mode.game.myEmpire['help'].append('EndTurn')
        self.mode.mainmenu.writeTextRoundEnds()
        self.mode.clearMyGui()
            
if __name__ == "__main__":
    myGui = QuestionEndRound('media')
    run()
    
    