# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipPanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel Contains the Ship data plus its associated sub data
# ---------------------------------------------------------------------------
import sys
import wx

import gridControl
import notebookControl
import anwp.war.ship
import anwp.war.quad
import anwp.war.weapon
import anwp.war.component

class ShipPanel(wx.Panel):
    def __init__(self, parent, id, log, galaxy):
        wx.Panel.__init__(self, parent)
        self.selectedID = ''
        self.galaxy = galaxy
        self.SetAutoLayout(True)
        self.SetBackgroundColour("ORANGE")
        
        self.mainGrid = gridControl.GridControlParent(self, log, anwp.war.ship.Ship({}), 1)
        self.mainGrid.loadData(galaxy.ships, 1)

        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 20)
        self.mainGrid.SetConstraints(lc)
        
        self.subNotebook = QuadNotebook(self, id, log, galaxy)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.mainGrid, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 65)
        self.subNotebook.SetConstraints(lc)
        
        self.subQuadNotebook = SubQuadNotebook(self, id, log, galaxy)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.subNotebook, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.SameAs(self, wx.Bottom, 10)
        self.subQuadNotebook.SetConstraints(lc)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
        
    def SaveData(self):
        """Save all Data currently shown"""
        self.mainGrid.SaveGridData(self.galaxy, 'ships')
        
        if self.subNotebook.quads <> None:
            self.subNotebook.quadsGrid.SaveGridData(self.subNotebook.quads, '')
            self.subQuadNotebook.componentsGrid.SaveGridData(self.subNotebook.quads[self.subNotebook.selectedID], 'components')
            self.subQuadNotebook.weaponsGrid.SaveGridData(self.subNotebook.quads[self.subNotebook.selectedID], 'weapons')

class QuadNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        self.parent = parent
        self.selectedID = ''
        self.quads = None
        
        # create quad grid
        self.quadsGrid = gridControl.GridControlQuad(self, log, anwp.war.quad.Quad({}), 5)
        self.AddPage(self.quadsGrid, 'quads')
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
    
    def populateTabs(self, id):
        """Take given id and populate with data"""
        try:
            myShip = self.galaxy.ships[id]
            self.quads = myShip.quads
            self.quadsGrid.loadData(self.quads, 1)
        except:
            self.quads = None

class SubQuadNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        self.parent = parent
        
        # init tabs and grids
        d1 = ('components', anwp.war.component.Component({}), 1)
        d2 = ('weapons', anwp.war.weapon.Weapon({}), 1)
        
        self.MakeTabs(d1, d2)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def populateTabs(self, id):
        """Take given id and populate with data"""
        try:
            myQuad = self.parent.subNotebook.quads[id]
            self.componentsGrid.loadData(myQuad.components, 1)
            self.weaponsGrid.loadData(myQuad.weapons, 1)
        except:
            pass

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        import anwp.func.storedata
        wx.Frame.__init__(self, parent, -1, "test", size=(1024,768))
        path = '../Database/ANW.anw'
        myGalaxy = anwp.func.storedata.loadFromFile(path)
        self.panel = ShipPanel(self, -1, log, myGalaxy)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

