# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# systemPanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel Contains the System data plus its associated sub data
# ---------------------------------------------------------------------------
import sys
import wx

import gridControl
import notebookControl
import anwp.aw.system
import anwp.aw.city
import anwp.aw.industry

class SystemPanel(wx.Panel):
    def __init__(self, parent, id, log, galaxy):
        wx.Panel.__init__(self, parent)
        self.selectedID = '1'
        self.galaxy = galaxy
        self.SetAutoLayout(True)
        self.SetBackgroundColour("MEDIUM ORCHID")
        
        self.mainGrid = gridControl.GridControlParent(self, log, anwp.aw.system.System({}), 1)
        self.mainGrid.loadData(galaxy.systems, 0)

        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 50)
        self.mainGrid.SetConstraints(lc)

        self.subNotebook = SubNotebook(self, id, log, galaxy, self.selectedID)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.mainGrid, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.SameAs(self, wx.Bottom, 10)
        self.subNotebook.SetConstraints(lc)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
    
    def SaveData(self):
        """Save all Data currently shown"""
        self.mainGrid.SaveGridData(self.galaxy, 'systems')
        if self.selectedID <> '':
            mySystem = self.galaxy.systems[self.selectedID]
            self.subNotebook.myCitiesGrid.SaveGridData(mySystem, 'myCities')
            self.subNotebook.myIndustryGrid.SaveGridData(mySystem, 'myIndustry')

class SubNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy, myID):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        
        # init tabs and grids
        d1 = ('myCities', anwp.aw.city.City({}), 1)
        d2 = ('myIndustry', anwp.aw.industry.Industry({}), 5)
        self.MakeTabs(d1, d2)
        self.populateTabs(myID)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def populateTabs(self, id):
        """Take given id and populate with data"""
        if id <> '':
            mySystem = self.galaxy.systems[id]
            self.myCitiesGrid.loadData(mySystem.myCities, 0)
            self.myIndustryGrid.loadData(mySystem.myIndustry, 5)

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        import anwp.func.storedata
        wx.Frame.__init__(self, parent, -1, "test", size=(1024,768))
        path = '../Database/ANW.anw'
        myGalaxy = anwp.func.storedata.loadFromFile(path)
        self.panel = SystemPanel(self, -1, log, myGalaxy)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

