# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testPanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel allows for testing for other panels
# ---------------------------------------------------------------------------
import wx

from anw.func import storedata

class TestPanel(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "test", size=(1024,768))
        path = '../Database/ANW1/ANW1.anw'
        self.myGalaxy = storedata.loadFromFile(path)
        self.panel = None
    
    def setPanel(self, panel):
        self.panel = panel