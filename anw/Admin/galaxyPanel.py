# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# galaxyPanel.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This Panel Contains the Galaxy data plus its associated sub data
# ---------------------------------------------------------------------------
import sys
import wx

import testPanel
import gridControl
import notebookControl
from anw.aw import galaxy, industrydata, traderoute, order, marketstat
from anw.war import componentdata, shiphulldata, dronehulldata, weapondata, regimentdata, captain

class GalaxyPanel(wx.Panel):
    def __init__(self, parent, id, log, myGalaxy):
        wx.Panel.__init__(self, parent)
        self.galaxy = myGalaxy
        self.SetAutoLayout(True)
        self.SetBackgroundColour("SIENNA")
        
        self.mainGrid = gridControl.GridControl(self, log, galaxy.Galaxy({}), 1)
        cellData = []
        cellData.append(myGalaxy.getAttributes(True))
        self.mainGrid.PopulateGrid(self.mainGrid.header, cellData)

        lc = wx.LayoutConstraints()
        lc.top.SameAs(self, wx.Top, 10)
        lc.left.SameAs(self, wx.Left, 10)
        lc.right.SameAs(self, wx.Right, 10)
        lc.bottom.PercentOf(self, wx.Bottom, 10)
        self.mainGrid.SetConstraints(lc)

        self.subNotebook = SubNotebook(self, id, log, myGalaxy)
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
        cellData = self.mainGrid.GetCellValues()
        name = self.mainGrid.GetCellValue(0, 0)
        self.galaxy.setAttributes(self.mainGrid.GetDictValues(0))
        
        self.subNotebook.industrydataGrid.SaveGridData(self.galaxy, 'industrydata')
        self.subNotebook.tradeRoutesGrid.SaveGridData(self.galaxy, 'tradeRoutes')
        self.subNotebook.marketOrdersGrid.SaveGridData(self.galaxy, 'marketOrders')
        self.subNotebook.marketStatsGrid.SaveGridData(self.galaxy, 'marketStats')
        self.subNotebook.componentdataGrid.SaveGridData(self.galaxy, 'componentdata')
        self.subNotebook.shiphulldataGrid.SaveGridData(self.galaxy, 'shiphulldata')
        self.subNotebook.dronehulldataGrid.SaveGridData(self.galaxy, 'dronehulldata')
        self.subNotebook.weapondataGrid.SaveGridData(self.galaxy, 'weapondata')
        self.subNotebook.regimentdataGrid.SaveGridData(self.galaxy, 'regimentdata')
        self.subNotebook.captainsGrid.SaveGridData(self.galaxy, 'captains')

class SubNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log, galaxy):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        self.galaxy = galaxy
        
        # init tabs and grids
        d1 = ('industrydata', industrydata.IndustryData({}), 1)
        d2 = ('tradeRoutes', traderoute.TradeRoute({}), 5)
        d3 = ('marketOrders', order.MarketOrder({}), 5)
        d4 = ('marketStats', marketstat.MarketStat({}), 5)
        d6 = ('componentdata', componentdata.ComponentData({}), 1)
        d7 = ('shiphulldata', shiphulldata.ShipHullData({}), 1)
        d8 = ('dronehulldata', shiphulldata.ShipHullData({}), 1)
        d9 = ('weapondata', weapondata.WeaponData({}), 1)
        d10 = ('regimentdata', regimentdata.RegimentData({}), 1)
        d11 = ('captains', captain.Captain({}), 5)
        
        self.MakeTabs(d1, d2, d3, d4, d6, d7, d8, d9, d10, d11)
        
        # populate with data
        self.industrydataGrid.loadData(self.galaxy.industrydata, 0)
        self.tradeRoutesGrid.loadData(self.galaxy.tradeRoutes, 5)
        self.marketOrdersGrid.loadData(self.galaxy.marketOrders, 5)
        self.marketStatsGrid.loadData(self.galaxy.marketStats, 5)
        self.componentdataGrid.loadData(self.galaxy.componentdata, 0)
        self.shiphulldataGrid.loadData(self.galaxy.shiphulldata, 0)
        self.dronehulldataGrid.loadData(self.galaxy.dronehulldata, 0)
        self.weapondataGrid.loadData(self.galaxy.weapondata, 0)
        self.regimentdataGrid.loadData(self.galaxy.regimentdata, 0)
        self.captainsGrid.loadData(self.galaxy.captains, 5)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

class TestFrame(testPanel.TestPanel):
    def __init__(self, parent, log):
        testPanel.TestPanel.__init__(self, parent, log)
        self.setPanel(GalaxyPanel(self, -1, log, self.myGalaxy))

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

