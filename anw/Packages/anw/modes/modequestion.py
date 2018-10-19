# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# modequestion.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Ask the player a question
# ---------------------------------------------------------------------------
import types
import mode
from anw.gui import textonscreen, questionendround
from anw.func import globals

class ModeQuestion(mode.Mode):
    """This is the Question Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.cameraPos = (0,-20, 0)
        self.enableMouseCamControl = 0
        self.resetCamera()
        self.name = 'QUESTION'
        self.title = None
        self.createMainMenu('E')
        self.questiongui = None
        self.endMyTurn()
    
    def clearMyGui(self):
        self.removeMyGui('title')
        self.removeMyGui('questiongui')
        
    def createQuestionEndRound(self):
        self.printTitle('You are the last to end your turn and the round will end now, please choose an option:', 2)
        self.questiongui = questionendround.QuestionEndRound(self.guiMediaPath)
        self.gui.append(self.questiongui)
        
    def printTitle(self, title, y):
        """Print the chart title"""
        self.title = textonscreen.TextOnScreen(self.guiMediaPath, str(title), 0.35)
        self.title.writeTextToScreen(-5, 20, y, 30)
        self.title.setColor(globals.colors['guiyellow'])
        self.gui.append(self.title)
        
    def endMyTurn(self):
        """End the players Turn"""
        try:
            result = self.game.server.endEmpireTurn(self.game.authKey)
            if result == 0:
                if 'EndTurn' not in self.game.myEmpire['help']:
                    self.modeMsgBox('You have now un-ended your turn')
                    self.game.myEmpire['help'].append('EndTurn')
                else:
                    self.modeMsgBox('Your turn has been ended, thankyou')
                    self.game.myEmpire['help'].remove('EndTurn')
                self.mainmenu.writeTextRoundEnds()
            elif type(result) == types.StringType:
                self.modeMsgBox(result)
            else:
                self.createQuestionEndRound()
                self.questiongui.setMyMode(self)
        except:
            self.modeMsgBox('endMyTurn->Connection to Server Lost')
        
    def endAndWait(self):
        """End Turn and wait for it to end"""
        result = self.game.server.endRound(self.game.authKey)
        self.game.server.logout(self.game.authKey)
        from anw.modes.modelogin import ModeLogin
        newMode = ModeLogin(self.game, 200)
        self.game.enterMode(newMode)
        
        
    