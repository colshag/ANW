# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# techline.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a line that joins two points in tech mode
# this is only needed because line cannot rotate properly in tech mode
# ---------------------------------------------------------------------------
from anw.gui import line
from anw.func import funcs, globals

class TechLine(line.Line):
    """A Tech Line"""
    def __init__(self, path, (x1,z1), (x2,z2), complete):
        self.complete = complete
        line.Line.__init__(self, path, (x1,z1), (x2,z2), 'square', width=0.05)
    
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        if self.complete == 1:
            self.setGlow()
        self.reSize()
        self.setPos()
        self.rotate()
        
