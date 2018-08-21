# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# systemPanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel Contains the System data plus its associated sub data
# ---------------------------------------------------------------------------
import sys
import wx

import testPanel
import gridControl
import notebookControl
from anw.aw import system

class SystemPanel(wx.Panel):
    def __init__(self, parent, id, log, galaxy):
        wx.Panel.__init__(self, parent)
        self.selectedID = '1'
        self.galaxy = galaxy
        self.SetAutoLayout(True)
        self.SetBackgroundColour("MEDIUM ORCHID")
        
        self.mainGrid = gridControl.GridControlParent(self, log, system.System({}), 1)
        self.mainGrid.loadData(galaxy.systems, 0)

        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.bottom.SameAs(self, wx.Bottom, 10)
        self.mainGrid.SetConstraints(lc)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
    
    def SaveData(self):
        """Save all Data currently shown"""
        self.mainGrid.SaveGridData(self.galaxy, 'systems')
        if self.selectedID != '':
            mySystem = self.galaxy.systems[self.selectedID]

class TestFrame(testPanel.TestPanel):
    def __init__(self, parent, log):
        testPanel.TestPanel.__init__(self, parent, log)
        self.setPanel(SystemPanel(self, -1, log, self.myGalaxy))

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

