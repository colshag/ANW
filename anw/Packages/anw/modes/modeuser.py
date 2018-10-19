# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# modeuser.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Ask the player a question
# ---------------------------------------------------------------------------
import mode
import types
from anw.gui import textonscreen, questionsurrender
from anw.func import globals

class ModeUser(mode.Mode):
    """This is the User Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.cameraPos = (0,-20, 0)
        self.enableMouseCamControl = 0
        self.resetCamera()
        self.name = 'USER'
        self.title = None
        self.createMainMenu('U')
        self.questiongui = None
        self.createQuestionSurrender()
    
    def clearMyGui(self):
        self.removeMyGui('title')
        self.removeMyGui('questiongui')
        
    def createQuestionSurrender(self):
        self.printTitle('If you are finding that you do not have the time to play, or you feel that there is no chance of victory you can choose to surrender at any time:', 2)
        self.questiongui = questionsurrender.QuestionSurrender(self.guiMediaPath)
        self.questiongui.setMyMode(self)
        self.gui.append(self.questiongui)
        
    def printTitle(self, title, y):
        self.title = textonscreen.TextOnScreen(self.guiMediaPath, str(title), 0.35)
        self.title.writeTextToScreen(-5, 20, y, 30)
        self.title.setColor(globals.colors['guiyellow'])
        self.gui.append(self.title)
    
    def surrender(self):
        """Player is surrendering from the game"""
        try:
            serverResult = self.game.server.surrender(self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.exitGame()
        except:
            self.modeMsgBox('surrender->Connection to Server Lost, Login Again')
      