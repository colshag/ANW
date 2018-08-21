# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modehistory.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the view past battles
# ---------------------------------------------------------------------------
import random

import mode
from anw.func import storedata, globals, root, funcs
from anw.gui import buttonlist
from anw.war import shipsimulator

class ModeHistory(mode.Mode, root.Root):
    """This represents the View Battles Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.enableMouseCamControl = 0
        self.resetCamera()
        self.name = 'HISTORY'
        self.createMainMenu('W')
        self.shipBattle = None
        self.battleInfo = None
        self.createBattleInfoFrame()
        self.populateBattleInfo()
        
    def createBattleInfoFrame(self):
        """Build the Mail Info Frame"""
        self.battleInfo = buttonlist.ButtonList(self.guiMediaPath, 'Choose a Ship Battle to View:', 1.5, 0.8)
        self.battleInfo.setMyPosition(0, 0.40)
        self.battleInfo.setMyMode(self)
        self.battleInfo.setOnClickMethod('viewShipBattle')
        self.gui.append(self.battleInfo)
        
    def populateBattleInfo(self):
        """Fill Battle Info with all past battles"""
        for key in funcs.sortStringList(self.game.shipBattleDict.keys()):
            name = self.game.shipBattleDict[key]
            self.battleInfo.myScrolledList.addItem(text=name,extraArgs=key)
    
    def getShipBattle(self, shipBattleKey):
        """Ask the Server for the Ship Battle Object"""
        try:
            serverResult = self.game.server.getShipBattle(self.game.authKey, shipBattleKey)
            if type(serverResult) == -1:
                self.modeMsgBox('getShipBattle->error')
            else:
                self.shipBattle = storedata.loadFromString(serverResult)
        except:
            self.modeMsgBox('getShipBattle->Connection to Server Lost')
    
    def viewShipBattle(self, battleID, index, button):
        """Actually View the ShipBattle"""
        self.getShipBattle(battleID)
        if self.shipBattle == None:
            self.modeMsgBox('please select a ship battle to view')
        else:
            self.game.app.enableMouseCamControl()
            newMode = shipsimulator.ShipSimulator(self.game, self.shipBattle)
            self.game.enterMode(newMode)
            
    def shareShipBattle(self, empireID, shipBattleKey):
        """Share the ShipBattle selected with another Empire"""
        try:
            serverResult = self.game.server.shareShipBattle(self.game.authKey, empireID, shipBattleKey)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Battle can now be viewed by Empire:%s' % self.game.allEmpires[empireID]['name'])
        except:
            self.modeMsgBox('shareShipBattle->Connection to Server Lost, Login Again')
