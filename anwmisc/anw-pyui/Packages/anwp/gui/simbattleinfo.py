# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# simbattleinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows player to build simulated battles for ship/fleet testing
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.funcs

class SimBattleInfoFrame(guibase.BaseInfoFrame):
    """Displays Sim Battle Information"""  
    def __init__(self, mode, app, title='Create a Simulated Ship Battle'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(SimBattleInfoPanel(self))
        self.panel.populate()
            
class SimBattleInfoPanel(guibase.BasePanel):
    """Panel for simulating ship Battles"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 3
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # fleets
        n = 0
        self.lbl = pyui.widgets.Label(text='FLEETS: (Team - Name - Grid - Ships)', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstFleets = pyui.widgets.ListBox(self.onFleetSelected, None, 100, 100, 0)
        self.addChild(self.lstFleets, (0, n+1, 4, 5+x))
        self.btnNewFleet1 = pyui.widgets.Button('New Fleet 1', self.onNewFleet1)
        self.addChild(self.btnNewFleet1, (0, n+6+x, 2, 1))
        self.btnNewFleet2 = pyui.widgets.Button('New Fleet 2', self.onNewFleet2)
        self.addChild(self.btnNewFleet2, (2, n+6+x, 2, 1))
        self.btnConfigFleet = pyui.widgets.Button('Configure Fleet', self.onConfigFleet)
        self.addChild(self.btnConfigFleet, (0, n+7+x, 2, 1))
        self.btnChooseQuad = pyui.widgets.Button('New Map Grid', self.onChooseQuad)
        self.addChild(self.btnChooseQuad, (2, n+7+x, 2, 1))
        
        # ships
        n = n+9+x
        self.lbl = pyui.widgets.Label(text='SHIPS IN FLEET:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstShips = pyui.widgets.ListBox(self.onShipSelected, None, 100, 100, 0)
        self.addChild(self.lstShips, (0, n+1, 4, 4+x))
        self.btnShipInfo = pyui.widgets.Button('Ship Info', self.onShipInfo)
        self.addChild(self.btnShipInfo, (0, n+5+x, 2, 1))
        self.btnRemoveShip = pyui.widgets.Button('Remove Ship', self.onRemoveShip)
        self.addChild(self.btnRemoveShip, (2, n+5+x, 2, 1))
        
        # Choose ship design
        n = n+7+x
        self.lbl = pyui.widgets.Label(text='CHOOSE SHIP DESIGN:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstShipDesigns = pyui.widgets.ListBox(self.onDesignSelected, None, 100, 100, 0)
        self.addChild(self.lstShipDesigns, (0, n+1, 4, 5+x))
        self.btnAddShip = pyui.widgets.Button('Add Ship to Fleet', self.onAddShip)
        self.addChild(self.btnAddShip, (0, n+6+x, 2, 1))
        self.btnViewBattle = pyui.widgets.Button('View Battle', self.onViewBattle)
        self.addChild(self.btnViewBattle, (0, n+7+x, 2, 1))
        self.lbl = pyui.widgets.Label('Simulations Left This Turn:', type=1)
        self.addChild(self.lbl, (0, n+8+x, 3, 1))
        self.lblSimsLeft = pyui.widgets.Label('0', type=2)
        self.addChild(self.lblSimsLeft, (3, n+8+x, 1, 1))
        
        # pack widgets
        self.pack

    def buildFleetData(self):
        """Take current shipBattle object and display fleets from it"""
        d = {}
        for fleetID, myFleet in self.frame.mode.fleets.iteritems():
            d[fleetID] = '%s - %s (Grid:%d)(Quad:%d)(Ships:%d)' % (myFleet.empireID, myFleet.name, myFleet.systemGrid, myFleet.quadrant, len(myFleet.ships.keys()))
        return d
    
    def buildDesignData(self):
        """Display all available Starship Designs"""
        d = {}
        shipDesigns = self.frame.mode.game.shipDesigns
        myDesignKeys = anwp.func.funcs.sortStringList(shipDesigns.keys())
        for id in myDesignKeys:
            shipDesignTuple = shipDesigns[id]
            d[id] = '%s' % shipDesignTuple[0]
        return d
    
    def buildShipsInFleetData(self, fleetID):
        """Take all Ships contained within fleet"""
        d = {}
        myFleet = self.frame.mode.fleets[fleetID]
        for shipID, myShip in myFleet.ships.iteritems():
            d[shipID] = '%d:%s' % (myShip.position, myShip.name)
        return d
    
    def clearPanel(self):
        """Clear Panel Info"""
        # disable buttons, clear data
        self.btnChooseQuad.disable()
        self.btnConfigFleet.disable()
        self.btnShipInfo.disable()
        self.btnAddShip.disable()
        self.btnRemoveShip.disable()
        self.lstFleets.clear()
        self.lstShips.clear()
        self.lstShipDesigns.clear()
  
    def onAddShip(self, item):
        """Add Ship to Fleet selected"""
        self.frame.mode.createShip(self.lstFleets.getSelectedItem().data, self.lstShipDesigns.getSelectedItem().data)
        self.refreshShipList()
        self.refreshFleetList()
  
    def onConfigFleet(self, item):
        """config fleet for simulation"""
        self.frame.mode.createFleetInfoFrame(self.lstFleets.getSelectedItem().data)
  
    def onChooseQuad(self, item):
        """Choose map grid quadrant"""
        self.frame.mode.destroyTempFrames()
        self.frame.mode.createGetGridFrame(3, 6, 'Select Map Grid Quadrant')
    
    def onDesignSelected(self, item):
        """Select Ship Design"""
        if not item:
            self.btnAddShip.disable()
            self.frame.mode.destroyTempFrames()
        else:
            if self.lstFleets.selected <> -1:
                self.btnAddShip.enable()
  
    def onNewFleet1(self, item):
        """Add a new fleet to simulation"""
        self.frame.mode.createFleet('1')
        self.populate()
    
    def onNewFleet2(self, item):
        """Add a new fleet to simulation"""
        self.frame.mode.createFleet('2')
        self.populate()
  
    def onRemoveShip(self, item):
        """Remove Ship from simulation"""
        self.frame.mode.removeShip(self.lstFleets.getSelectedItem().data,
                                   self.lstShips.getSelectedItem().data)
        self.refreshShipList()
        self.refreshFleetList()
        self.btnRemoveShip.disable()
        self.btnShipInfo.disable()
  
    def onShipInfo(self, item):
        """Open Ship Info Panel"""
        if self.lstFleets.selected <> -1:            
            fleetID = self.lstFleets.getSelectedItem().data
            myFleet = self.frame.mode.fleets[fleetID]
            shipID = self.lstShips.getSelectedItem().data
            myShip = myFleet.ships[shipID]
            self.frame.mode.createShipInfoFrameFromShip(myShip)
    
    def onFleetSelected(self, item):
        """Select item from List"""
        if not item:
            self.populate()
        else:
            self.refreshShipList()
            self.btnConfigFleet.enable()
            self.btnChooseQuad.enable()
    
    def onViewBattle(self, item):
        """View Battle Selected"""
        self.frame.mode.genShipBattle()
    
    def onShipSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnShipInfo.disable()
            self.btnRemoveShip.disable()
            self.frame.mode.destroyTempFrames()
        else:
            self.btnShipInfo.enable()
            self.btnRemoveShip.enable()
    
    def populate(self):
        """Populate frame with new data"""
        self.clearPanel()
        
        # load resources
        try:
            self.frame.mode.destroyTempFrames()
            myFleets = self.buildFleetData()
            myDesigns = self.buildDesignData()
            self.lblSimsLeft.setText(str(self.frame.mode.game.myEmpire['simulationsLeft']))
        except:
            # this allows for testing panel outside game
            myFleets = myDesigns = self.testDict
        
        # populate lists
        self.refreshFleetList()
        self.populateListbox(self.lstShipDesigns, myDesigns)
    
    def refreshShipList(self):
        """Refresh the ship list"""
        shipID = -1
        if self.lstFleets.selected <> -1:
            try:
                shipID = self.lstShips.getSelectedItem().data
            except:
                shipID = -1
            myShips = self.buildShipsInFleetData(self.lstFleets.getSelectedItem().data)
            self.populateListbox(self.lstShips, myShips)
            if shipID <> -1:
                self.lstShips.setSelectedItemByData(shipID)
    
    def refreshFleetList(self):
        """Refresh the fleet list"""
        fleetID = -1
        try:
            fleetID = self.lstFleets.getSelectedItem().data
        except:
            fleetID = -1
        myFleets = self.buildFleetData()
        self.populateListbox(self.lstFleets, myFleets)
        if fleetID <> -1:
            self.lstFleets.setSelectedItemByData(fleetID)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Sim Battle Info Panel')
    app = run.TestApplication(width, height)
    frame = SimBattleInfoFrame(None, app)
    frame.panel.populate()
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
