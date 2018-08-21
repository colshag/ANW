# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# empirePanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel Contains the Empire data plus its associated sub data
# ---------------------------------------------------------------------------
import sys
import wx
import string

import testPanel
import gridControl
import notebookControl
from anw.aw import empire, tech, order, mail, diplomacy
from anw.war import ship, shipdesign, dronedesign, quad, weapon, component

class EmpirePanel(wx.Panel):
    def __init__(self, parent, id, log, galaxy):
        wx.Panel.__init__(self, parent)
        self.selectedID = '1'
        self.galaxy = galaxy
        self.SetAutoLayout(True)
        self.SetBackgroundColour("SKY BLUE")
        
        self.mainGrid = gridControl.GridControlParent(self, log, empire.Empire({}), 1)
        self.mainGrid.loadData(galaxy.empires, 0)

        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 20)
        self.mainGrid.SetConstraints(lc)

        self.subNotebook = SubNotebook(self, id, log, galaxy, self.selectedID)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.mainGrid, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 50)
        self.subNotebook.SetConstraints(lc)
        
        self.quadNotebook = QuadNotebook(self, id, log, galaxy)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.subNotebook, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 65)
        self.quadNotebook.SetConstraints(lc)
        
        self.subQuadNotebook = SubQuadNotebook(self, id, log, galaxy)
        lc = wx.LayoutConstraints()
        lc.top.Below(self.quadNotebook, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.bottom.SameAs(self, wx.Bottom, 10)
        self.subQuadNotebook.SetConstraints(lc)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
        
    def SaveData(self):
        """Save all Data currently shown"""
        self.mainGrid.SaveGridData(self.galaxy, 'empires')
        if self.selectedID != '':
            myEmpire = self.galaxy.empires[self.selectedID]
            self.subNotebook.techTreeGrid.SaveGridData(myEmpire, 'techTree')
            self.subNotebook.techOrdersGrid.SaveGridData(myEmpire, 'techOrders')
            self.subNotebook.industryOrdersGrid.SaveGridData(myEmpire, 'industryOrders')
            self.subNotebook.mailBoxGrid.SaveGridData(myEmpire, 'mailBox')
            self.subNotebook.shipDesignsGrid.SaveGridData(myEmpire, 'shipDesigns')
            self.subNotebook.diplomacyGrid.SaveGridData(myEmpire, 'diplomacy')
        
        if self.quadNotebook.quads != None:
            self.quadNotebook.quadsGrid.SaveGridData(self.quadNotebook.quads, '')
            self.subQuadNotebook.componentsGrid.SaveGridData(self.quadNotebook.quads[self.quadNotebook.selectedID], 'components')
            self.subQuadNotebook.weaponsGrid.SaveGridData(self.quadNotebook.quads[self.quadNotebook.selectedID], 'weapons')

class SubNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy, myID):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        self.parent = parent
        
        # init tabs and grids
        d1 = ('techTree', tech.Tech({}), 1)
        d2 = ('techOrders', order.Order({}), 5)
        d3 = ('industryOrders', order.IndustryOrder({}), 5)
        d4 = ('mailBox', mail.Mail({}), 5)
        d5 = ('diplomacy', diplomacy.Diplomacy({}), 1)
        
        self.MakeTabs(d1, d2, d3, d4, d5)
        
        # build these tabs with ability to populate Notebooks below them
        self.shipDesignsGrid = gridControl.GridControlShipDesign(self, log, shipdesign.ShipDesign({}), 5)
        self.AddPage(self.shipDesignsGrid, 'shipDesigns')
        self.droneDesignsGrid = gridControl.GridControlDroneDesign(self, log, dronedesign.DroneDesign({}), 5)
        self.AddPage(self.droneDesignsGrid, 'droneDesigns')
        
        self.populateTabs(myID)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def populateTabs(self, id):
        """Take given id and populate with data"""
        myEmpire = self.galaxy.empires[id]
        self.techTreeGrid.loadData(myEmpire.techTree, 0)
        self.techOrdersGrid.loadData(myEmpire.techOrders, 5)
        self.industryOrdersGrid.loadData(myEmpire.industryOrders, 5)
        self.mailBoxGrid.loadData(myEmpire.mailBox, 5)
        self.diplomacyGrid.loadData(myEmpire.diplomacy, 0)
        self.shipDesignsGrid.loadData(myEmpire.shipDesigns, 5)
        self.droneDesignsGrid.loadData(myEmpire.droneDesigns, 5)

class QuadNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        self.parent = parent
        self.selectedID = ''
        self.quads = None
        
        # create quad grid
        self.quadsGrid = gridControl.GridControlQuad(self, log, quad.Quad({}), 5)
        self.AddPage(self.quadsGrid, 'quads')
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def setSelectedID(self, id):
        """Set the selected ID"""
        self.selectedID = id
    
    def populateShipDesignQuads(self, id):
        """Take given id and populate with data"""
        myEmpire = self.galaxy.empires[self.parent.selectedID]
        try:
            myShipDesign = myEmpire.shipDesigns[id]
            self.quads = myShipDesign.quads
            self.quadsGrid.loadData(self.quads, 1)
        except:
            self.quads = None
    
    def populateDroneDesignQuads(self, id):
        """Take given id and populate with data"""
        myEmpire = self.galaxy.empires[self.parent.selectedID]
        try:
            myDroneDesign = myEmpire.droneDesigns[id]
            quad = quad.Quad({})
            quad.components = myDroneDesign.components
            quad.weapons = myDroneDesign.weapons
            self.quads = {'drone':quad}
            self.quadsGrid.loadData(self.quads, 1)
        except:
            self.quads = None

class SubQuadNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        self.parent = parent
        
        # init tabs and grids
        d1 = ('components', component.Component({}), 1)
        d2 = ('weapons', weapon.Weapon({}), 1)
        
        self.MakeTabs(d1, d2)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def populateTabs(self, id):
        """Take given id and populate with data"""
        try:
            myQuad = self.parent.quadNotebook.quads[id]
            self.componentsGrid.loadData(myQuad.components, 1)
            self.weaponsGrid.loadData(myQuad.weapons, 1)
        except:
            pass

class TestFrame(testPanel.TestPanel):
    def __init__(self, parent, log):
        testPanel.TestPanel.__init__(self, parent, log)
        self.setPanel(EmpirePanel(self, -1, log, self.myGalaxy))

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

