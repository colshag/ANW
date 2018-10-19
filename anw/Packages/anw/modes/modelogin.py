# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# modelogin.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Login Mode in ANW
# ---------------------------------------------------------------------------
import mode
from anw.modes import modemail
from direct.task import Task
from anw.func import globals
    
class ModeLogin(mode.Mode):
    """This is the Login Mode, this should only come up on login error"""
    def __init__(self, game, wait):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'LOGIN'
        self.myLogo = self.loadObject(tex='cosmica', depth=300, glow=1)
        self.sims.append(self.myLogo)
        self.count = wait
        taskMgr.add(self.login, 'loginTask')
        
    def login(self, task):
        """Check if we can login"""
        if self.count <= 0:
            self.game.loginToGame()
            return Task.done
        else:
            self.count -= 1
            return Task.cont

    def enterMode(self):
        """Do not accept Mouse Events"""
        