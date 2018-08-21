# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# gridControl.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a Grid Control used in ANW Admin
# ---------------------------------------------------------------------------
import wx
import wx.grid as gridlib
import wx.lib.mixins.grid as mixins
import string

from anw.func import root, funcs
from anw.aw import empire, system, traderoute, industrydata, marketstat, order
from anw.war import componentdata, shiphulldata, weapondata, captain, component
from anw.war import regiment, quad, ship, shipdesign, weapon

class GridControl(gridlib.Grid, mixins.GridAutoEditMixin):
    def __init__(self, parent, log, obj, spaces):
        gridlib.Grid.__init__(self, parent, -1)
        mixins.GridAutoEditMixin.__init__(self)
        self.log = log
        self.moveTo = None

        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.CreateGrid(5, 5)#, gridlib.Grid.SelectRows)
        self.EnableEditing(True)
        self.header = None
        self.blankList = None
        self.cells = None
        self.spaces = spaces
        self.obj = obj
        self.header = list(self.obj.defaultAttributes)
        self.blankList = self.obj.getAttributes(True)
        self.cells = list()
        self.PopulateGrid(self.header, self.cells, self.spaces)
        
        # attribute objects let you keep a set of formatting values
        # in one spot, and reuse them if needed
        self.cellHighlight = gridlib.GridCellAttr()
        self.cellHighlight.SetTextColour(wx.BLACK)
        self.cellHighlight.SetBackgroundColour(wx.RED)
        self.cellHighlight.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        # you can set cell attributes for the whole row (or column)
        self.SetColAttr(0, self.cellHighlight)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)

        # test all the events
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        ##self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        ##self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        ##self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)

        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        ##self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        ##self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        ##self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)

        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)

        ##self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)

        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)
    
    def loadData(self, dictData, num):
        """Load data into Grid"""
        cellData = []
        keyList = funcs.sortDictValues(dictData)
        for obj in keyList:
            cellData.append(obj.getAttributes(True))
        
        # populate grid
        self.PopulateGrid(self.header, cellData, num)
    
    def PopulateGrid(self, columns = [], rows = [], spaces = 0):
        """Populates the Grid by setting the Columns First then populating the Rows
        The Rows consists of a List within a List
        """
        # add blank cells to the end
        while spaces > 0:
            rows.append(self.blankList)
            spaces = spaces -1 
        
        # reset grid
        if self.GetNumberCols() > 1:
            self.DeleteCols(1,self.GetNumberCols())
        if self.GetNumberRows() > 1:
            self.DeleteRows(1,self.GetNumberRows())
        self.AppendCols(len(columns)-1)
        self.AppendRows(len(rows)-1)
        
        # set column names
        i = 0
        for item in columns:
            self.SetColLabelValue(i, item)
            i += 1
        
        # populate grid cells
        i = 0
        for list in rows:
            j = 0
            for item in list:
                self.SetCellValue(i, j, item)
                j += 1
            i += 1

    def GetCellValues(self):
        """Return all cell values as a list of lists"""
        list = []
        for i in range(0,self.GetNumberRows()):
            sublist = []
            for j in range(0,self.GetNumberCols()):
                sublist.append( self.GetCellValue(i, j) )
            list.append( sublist )
        return list
    
    def GetDictValues(self, row):
        """Given Row Number, Return Table Data as a Dict using Columns as Keys"""
        dict = {}
        for i in range(0,self.GetNumberCols()):
            dict[self.GetColLabelValue(i)] = self.GetCellValue(row, i)
        return dict
    
    def SaveGridData(self, obj, dictName):
        """Take Grid Data and assume the first Column is the id, save data into obj dict supplied"""
        cellData = self.GetCellValues()
        idDict = {}
        if dictName == '':
            dictObj = obj
        else:
            dictObj = getattr(obj, dictName)
        i = 0
        for list in cellData:
            try:
                id = str(list[0])
            except:
                id = 0
            if id != 0 and id != '':
                idDict[id] = 1
                gridValues = self.GetDictValues(i)
                if dictObj.has_key(id):
                    # existing obj in dict, modify its attributes
                    dictObj[id].setAttributes(gridValues)
                else:
                    # new obj in dict, create object dynamically
                    if dictName == 'empires':
                        newObj = empire.Empire(gridValues)
                    elif dictName == 'systems':
                        newObj = system.System(gridValues)
                    elif dictName == 'tradeRoutes':
                        newObj = traderoute.TradeRoute(gridValues)
                    elif dictName == 'industrydata':
                        newObj = industrydata.IndustryData(gridValues)
                    elif dictName == 'marketOrders':
                        newObj = order.MarketOrder(gridValues)
                    elif dictName == 'marketStats':
                        newObj = marketstat.MarketStat(gridValues)
                    elif dictName == 'componentdata':
                        newObj = componentdata.ComponentData(gridValues)
                    elif dictName == 'shiphulldata':
                        newObj = shiphulldata.ShipHullData(gridValues)
                    elif dictName == 'dronehulldata':
                        newObj = shiphulldata.DroneHullData(gridValues)
                    elif dictName == 'weapondata':
                        newObj = weapondata.WeaponData(gridValues)
                    elif dictName == 'captains':
                        newObj = captain.Captain(gridValues)
                    elif dictName == 'components':
                        newObj = component.Component(gridValues)
                    elif dictName == 'ships':
                        newObj = ship.Ship(gridValues)
                    elif dictName == 'regiments':
                        newObj = regiment.Regiment(gridValues)
                    elif dictName == 'ships':
                        newObj = ship.Ship(gridValues)
                    elif dictName == 'shipDesigns':
                        newObj = shipdesign.ShipDesign(gridValues)
                    elif dictName == 'weapons':
                        newObj = weapon.Weapon(gridValues)
                    # store obj in dict
                    dictObj[id] = newObj
            i += 1
            
        # delete items from dict in obj if their id is no longer in cellData list
        for id in dictObj.keys():
            if idDict.has_key(id):
                # obj found
                pass
            else:
                # id gone from list, delete obj from dict
                del dictObj[id]
    
    def OnCellLeftClick(self, evt):
        self.log.write("OnCellLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightClick(self, evt):
        self.log.write("OnCellRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellLeftDClick(self, evt):
        self.log.write("OnCellLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightDClick(self, evt):
        self.log.write("OnCellRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelRightClick(self, evt):
        self.log.write("OnLabelRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftDClick(self, evt):
        self.log.write("OnLabelLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelRightDClick(self, evt):
        self.log.write("OnLabelRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnRowSize(self, evt):
        self.log.write("OnRowSize: row %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnColSize(self, evt):
        self.log.write("OnColSize: col %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnRangeSelect(self, evt):
        if evt.Selecting():
            self.log.write("OnRangeSelect: top-left %s, bottom-right %s\n" %
                           (evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))
        evt.Skip()


    def OnCellChange(self, evt):
        self.log.write("OnCellChange: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        ##value = self.GetCellValue(evt.GetRow(), evt.GetCol())

        ##if value == 'no good':
            ##self.moveTo = evt.GetRow(), evt.GetCol()


    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None

        evt.Skip()


    def OnSelectCell(self, evt):
        self.log.write("OnSelectCell: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        ### Another way to stay in a cell that has a bad value...
        ##row = self.GetGridCursorRow()
        ##col = self.GetGridCursorCol()

        ##if self.IsCellEditControlEnabled():
            ##self.HideCellEditControl()
            ##self.DisableCellEditControl()

        ##value = self.GetCellValue(row, col)

        ##if value == 'no good 2':
            ##return  # cancels the cell selection
        
        evt.Skip()


    def OnEditorShown(self, evt):
        ##if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           ##wx.MessageBox("Are you sure you wish to edit this cell?",
                        ##"Checking", wx.YES_NO) == wx.NO:
            ##evt.Veto()
            ##return

        ##self.log.write("OnEditorShown: (%d,%d) %s\n" %
                       ##(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()


    def OnEditorHidden(self, evt):
        ##if evt.GetRow() == 6 and evt.GetCol() == 3 and \
           ##wx.MessageBox("Are you sure you wish to  finish editing this cell?",
                        ##"Checking", wx.YES_NO) == wx.NO:
            ##evt.Veto()
            ##return

        ##self.log.write("OnEditorHidden: (%d,%d) %s\n" %
                       ##(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()


    def OnEditorCreated(self, evt):
        self.log.write("OnEditorCreated: (%d, %d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetControl()))

class GridControlParent(GridControl):
    """This Grid will pass along objects to be populated by child Grid Controls"""
    def __init__(self, parent, log, obj, spaces):
        GridControl.__init__(self, parent, log, obj, spaces)
        self.parent = parent
    
    def OnLabelLeftClick(self, evt):
        """Return id of row selected"""
        try:
            row = evt.GetRow()
            if row != -1:
                value = self.GetCellValue(row, 0)
                self.parent.setSelectedID(value)
                self.parent.subNotebook.populateTabs(value)
                evt.Skip()
        except:
            pass

class GridControlShipDesign(GridControl):
    """This Grid will pass along objects to be populated by child Grid Controls"""
    def __init__(self, parent, log, obj, spaces):
        GridControl.__init__(self, parent, log, obj, spaces)
        self.parent = parent
    
    def OnLabelLeftClick(self, evt):
        """Return id of row selected"""
        try:
            row = evt.GetRow()
            if row != -1:
                value = self.GetCellValue(row, 0)
                self.parent.parent.quadNotebook.populateShipDesignQuads(value)
                evt.Skip()
        except:
            pass

class GridControlDroneDesign(GridControl):
    """This Grid will pass along objects to be populated by child Grid Controls"""
    def __init__(self, parent, log, obj, spaces):
        GridControl.__init__(self, parent, log, obj, spaces)
        self.parent = parent
    
    def OnLabelLeftClick(self, evt):
        """Return id of row selected"""
        try:
            row = evt.GetRow()
            if row != -1:
                value = self.GetCellValue(row, 0)
                self.parent.parent.quadNotebook.populateDroneDesignQuads(value)
                evt.Skip()
        except:
            pass

class GridControlQuad(GridControl):
    """This Grid will pass along objects to be populated by child Grid Controls"""
    def __init__(self, parent, log, obj, spaces):
        GridControl.__init__(self, parent, log, obj, spaces)
        self.parent = parent
    
    def OnLabelLeftClick(self, evt):
        """Return id of row selected"""
        try:
            row = evt.GetRow()
            if row != -1:
                value = self.GetCellValue(row, 0)
                self.parent.setSelectedID(value)
                self.parent.parent.subQuadNotebook.populateTabs(value)
                evt.Skip()
        except:
            pass

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Grid Control Test", size=(1024,768))
        self.grid = GridControl(self, log, root.Root({}), 4)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()