# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# armadainfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all controls for an armada of ships the galactic map
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.funcs
import anwp.func.globals

class ArmadaInfoFrame(guibase.BaseInfoFrame):
    """Displays Armada Information"""  
    def __init__(self, mode, app, title='Armada Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(ArmadaInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.armadaEntity = subject
        if self.armadaEntity.systemID <> self.currentID:
            # different armada populate panel
            self.currentID = self.armadaEntity.systemID
            
            # check if Armada owned by player
            if self.armadaEntity.myEmpireDict['id'] == self.mode.game.myEmpireID:
                self.setPanel(ArmadaInfoPanel(self))
            else:
                self.setPanel(OtherArmadaInfoPanel(self))
            
            # populate panel
            self.panel.populate(self.armadaEntity.myEmpireDict, self.armadaEntity.mySystemDict)
            
class ArmadaInfoPanel(guibase.BasePanel):
    """Panel for commanding Armadas"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 4
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # choose a ship
        n = 0
        self.lbl = pyui.widgets.Label(text='CHOOSE A SHIP:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstShips = pyui.widgets.ListBox(self.onShipSelected, None, 100, 100, 1)
        self.addChild(self.lstShips, (0, n+1, 4, 13+x))
        self.btnPositions = pyui.widgets.Button('Configure Ship Positions', self.onPositions)
        self.addChild(self.btnPositions, (0, n+14+x, 4, 1))
        self.btnSelectAll = pyui.widgets.Button('Select All Ships', self.onSelectAll)
        self.addChild(self.btnSelectAll, (0, n+15+x, 4, 1))
        
        # move ship to system
        n = n+17+x
        self.lbl = pyui.widgets.Label(text='MOVE SELECTED SHIPS TO:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstSystems = pyui.widgets.ListBox(self.onSystemSelected, None, 100, 100, 0)
        self.addChild(self.lstSystems, (0, n+1, 4, 9+x))
        self.btnMoveShips = pyui.widgets.Button('Move Ships to System', self.onMoveShips)
        self.addChild(self.btnMoveShips, (0, n+10+x, 4, 1))

        # pack widgets
        self.pack
    
    def buildShipData(self):
        """Display all player ships in Armada"""
        d = {}
        shipsAtSystem = self.frame.mode.game.myArmadas[self.mySystemDict['id']]
        shipsAtSystem = anwp.func.funcs.sortStringList(shipsAtSystem)
        for id in shipsAtSystem:
            myShipDict = self.frame.mode.game.myShips[id]
            damaged = 0
            # check for damaged ship
            s = '<%s>%s' % (id, myShipDict['name'])
            if myShipDict['strength'] < 100.0:
                s = '*' + s
            
            # check ship transport
            if myShipDict['maxTransport'] > 0:
                s = s + '(%s/%s)' % (myShipDict['currentTransport'], myShipDict['maxTransport'])
            else:
                transport = ''
            
            # ship captain rank
            rank = self.frame.mode.game.myCaptains[myShipDict['captainID']]['rank'][:3]
            s = rank + ':' + s
            
            # check for ship moved
            if myShipDict['fromSystem'] <> myShipDict['toSystem']:
                s = s + '<MOVED>'
                
            d[id] = s
        return d
    
    def buildSystemsAvailableData(self):
        """Display all Systems selected ships can move to"""
        self.lstSystems.clear()
        d = {}
        shipsSelected = self.lstShips.getMultiSelectedItems()
        
        # add all system ids of all ships selected
        for id in shipsSelected:
            myShipDict = self.frame.mode.game.myShips[id]
            for systemID in myShipDict['availSystems']:
                if d.has_key(systemID) == 0:
                    d[systemID] = self.frame.mode.game.allSystems[systemID]['name']
                    
        # remove system ids if any one ship cannot move to system
        for id in shipsSelected:
            myShipDict = self.frame.mode.game.myShips[id]
            for systemID in d.keys():
                if myShipDict['availSystems'].has_key(systemID) == 0:
                    del d[systemID]
        return d
    
    def clearPanel(self):
        """Clear Panel Info"""
        # disable buttons, clear data
        self.btnPositions.disable()
        self.btnSelectAll.disable()
        self.btnMoveShips.disable()
        self.lstShips.clear()
        self.lstSystems.clear()

    def onMoveShips(self, item):
        """Move fleet to selected system"""
        self.frame.mode.moveShips(self.lstShips.getMultiSelectedItems(), self.lstSystems.getSelectedItem().data)
    
    def onPositions(self, item):
        """Update the Ship Positions"""
        pass
    
    def onSelectAll(self, item):
        """Select All Ships"""
        ships = []
        for key in self.lstShips.dSelected.keys():
            self.lstShips.dSelected[key] = 1
        self.lstShips.setDirty()
        self.buildSystemsAvailableData()
        
    def onShipSelected(self, item):
        """Ship has been selected from list of ships"""
        self.frame.mode.destroyTempFrames()
        if item:
            mySystems = self.buildSystemsAvailableData()
            self.populateListbox(self.lstSystems, mySystems)
    
    def onSystemSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnMoveFleet.disable()
        else:
            if self.lstFleets.selected <> -1:
                self.btnMoveFleet.enable()
    
    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        self.clearPanel()
        
        # load resources
        try:
            self.frame.mode.destroyTempFrames()
            myShips = self.buildFleetData()
            self.frame.title = '%s: Armada Information' % mySystemDict['name']
        except:
            # this allows for testing panel outside game
            myShips = self.testDict
        
        # populate lists
        self.populateListbox(self.lstShips, myShips)

class OtherArmadaInfoPanel(guibase.BasePanel):
    """Panel for Viewing other Armadas"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 4
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # title
        n = 0
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (0, n, 1, 3))
        self.lblOwnedBy = pyui.widgets.Label(text='  Armada Owned By:', type=2)
        self.addChild(self.lblOwnedBy, (1, n+1, 3, 1))
        self.lblEmpireName = pyui.widgets.Label(text='')
        self.addChild(self.lblEmpireName, (1, n+2, 3, 1))
        
        # pack widgets
        self.pack
    
    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        
        # load resources
        try:
            self.frame.title = '%s: Armada Information' % mySystemDict['name']
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, myEmpireDict['imageFile'])
        except:
            pass
        
        self.pctEmpire.setFilename(myEmpirePict)
        self.lblEmpireName.setText('  %s' % myEmpireDict['name'])
        self.lblEmpireName.setColor(anwp.func.globals.colors[myEmpireDict['color1']])

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Armada Info Panel')
    app = run.TestApplication(width, height)
    frame = ArmadaInfoFrame(None, app)
    frame.panel.populate(None,None)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
