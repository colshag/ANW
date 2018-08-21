# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mainmenubuttons.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main menu button collection to traverse the different modes in the game
# ---------------------------------------------------------------------------
import string
import sys
import types

import direct.directbase.DirectStart
from anw.gui import textonscreen, questionendround
from rootbutton import RootButton
from anw.func import globals
        
class MainMenuButtons(RootButton):
    """The Main Button Menu"""
    def __init__(self, path, x=-0.35, y=0.95, name='main'):
        RootButton.__init__(self, path, x, y, name, ignoreShortcutButtons = [])
        self.allKeys = ['Q','W','E','R','T','Y','U','I','O']
        self.disableButtonIgnore = []
        self.disableButtonTime = 0
        self.lastDisabledButton = ''
        self.textTitle = None
        self.textRoundEnds = None
        self.empireSim = None
        self.textEmpireName = None
        self.textCR = None
        self.questionendround = None
        self.textRound = None

    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode
        
    def writeGameInfo(self):
        """Display all game info to user"""
        self.setMyColor()
        self.writeTextTitle()
        self.writeTextRoundEnds()
        self.createEmpireSim()
        self.writeEmpireName()
        self.writeCR()
    
    def writeTextTitle(self):
        """Write the Game Title"""
        text = 'Armada Net Wars'
        self.textTitle = textonscreen.TextOnScreen(self.path, text,
                                                   scale=0.03, font=5, parent=aspect2d)
        self.textTitle.writeTextToScreen(-1.0, 0, 0.95, 30)
        self.myWidgets.append(self.textTitle)
    
    def writeTextRoundEnds(self):
        """Write when the round will auto-end"""
        if self.textRoundEnds != None:
            self.removeMyWidget(self.textRoundEnds)
        if 'EndTurn' in self.mode.game.myEmpire['help']:
            text = 'PLEASE FINISH YOUR TURN\nROUND AUTO ENDS IN %d HRS' % self.game.myGalaxy['currentHoursLeft']
            color = 'guiyellow'
        else:
            text = 'THANKS FOR ENDING TURN\nROUND AUTO ENDS IN %d HRS' % self.game.myGalaxy['currentHoursLeft']
            color = 'guigreen'
        self.textRoundEnds = textonscreen.TextOnScreen(self.path, text,
                                                   scale=0.03, font=5, parent=aspect2d)
        self.textRoundEnds.writeTextToScreen(-1.0, -0.05, 0.92, 30)
        self.textRoundEnds.setColor(globals.colors[color])
        self.myWidgets.append(self.textRoundEnds)
        
    def createEmpireSim(self):
        """Display Empire Symbol"""
        self.empireSim = loader.loadModelCopy('%s/plane' % self.path)
        self.empireSim.setScale(0.08)
        self.empireSim.reparentTo(aspect2d)
        self.empireSim.setTransparency(1)
        tex = loader.loadTexture('%s/empire%s.png' % (self.path, self.game.myEmpireID))
        self.empireSim.setTexture(tex, 0)
        self.empireSim.setPos(0.55, 0, 0.95)
        self.empireSim.setColor(self.color)
        self.myWidgets.append(self.empireSim)
        
    def writeEmpireName(self):
        """Write the Empire Name"""
        text = self.game.myEmpire['player']
        self.textEmpireName = textonscreen.TextOnScreen(self.path, text,
                                                   scale=0.03, font=5, parent=aspect2d)
        self.textEmpireName.writeTextToScreen(0.6, 0, 0.95, 30)
        self.textEmpireName.setColor(self.color)
        self.myWidgets.append(self.textEmpireName)
        self.textRound = textonscreen.TextOnScreen(self.path, 'Round:  %s' % self.game.currentRound,
                                                   scale=0.03, font=5, parent=aspect2d)
        self.textRound.writeTextToScreen(0.60, 0, 0.89, 30)
        self.textRound.setColor(globals.colors['guiwhite'])
        self.myWidgets.append(self.textRound)
    
    def writeCR(self):
        """Write the Player Information"""
        text = ''
        self.textCR = textonscreen.TextOnScreen(self.path, text,
                                                   scale=0.03, font=5, parent=aspect2d)
        self.textCR.writeTextToScreen(0.6, 0, 0.92, 30)
        if self.game.myEmpire['CR'] > 100000:
            self.textCR.setColor(globals.colors['guigreen'])
        elif self.game.myEmpire['CR'] > 0:
            self.textCR.setColor(globals.colors['guiyellow'])
        else:
            self.textCR.setColor(globals.colors['guired'])
        self.updateCR()
        self.myWidgets.append(self.textCR)
    
    def updateCR(self):
        """update credits on screen"""
        self.textCR.myText.setText('CREDITS = %d ' % self.game.myEmpire['CR'])
    
    def createButtons(self):
        """Create all Buttons in desired order and position"""
        for key in ['Q','W','R','T','Y','U','I','O','E']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
    
    def pressQ(self):
        """Quit the game"""
        self.mode.exitGame()
    
    def pressW(self):
        """Enter the Battle Mode"""
        from anw.modes.modehistory import ModeHistory
        self.enterMode(ModeHistory)
    
    def pressE(self):
        """End player turn"""
        from anw.modes.modequestion import ModeQuestion
        self.enterMode(ModeQuestion)
    
    def pressT(self):
        """Enter the Tech Mode"""
        from anw.modes.modetech import ModeTech
        self.enterMode(ModeTech)
    
    def pressR(self):
        """Enter the Map Mode"""
        from anw.modes.modemap import ModeMap
        self.enterMode(ModeMap)
    
    def pressI(self):
        """Enter the Design Mode"""
        from anw.modes.modedesign import ModeDesign
        self.enterMode(ModeDesign)
    
    def pressU(self):
        """Enter the User Mode"""
        from anw.modes.modeuser import ModeUser
        self.enterMode(ModeUser)
    
    def pressY(self):
        """Enter the Mail Mode"""
        from anw.modes.modemail import ModeMail
        self.enterMode(ModeMail)
    
    def pressO(self):
        """Enter the Market Mode"""
        from anw.modes.modemarketstats import ModeMarketStats
        self.enterMode(ModeMarketStats)
    
    def pressButton(self, key):
        """Called when button is pressed or shortcut key is pressed"""
        if key not in self.disabledButtons:
            myMethod = getattr(self, 'press' + key)
            myMethod()
            self.enableLastButton(key)
            self.checkDisableButton(key)
            if self.mode != None:
                self.mode.playSound('beep02')
    
    def enableLastButton(self, key):
        """Enable the last pressed button, set the next one"""
        if self.lastDisabledButton != '':
            self.enableButton(self.lastDisabledButton)
        self.lastDisabledButton = key
    
    def enterMode(self, myMode):
        """Enter the new mode"""
        newMode = myMode(self.game)
        self.game.enterMode(newMode)
        
if __name__ == "__main__":
    mainMenuButtons = MainMenuButtons('media')
    run()