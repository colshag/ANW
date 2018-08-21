# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# pastbattleinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all viewable past battles from galaxy
# ---------------------------------------------------------------------------
import pyui
import guibase

class PastBattleInfoFrame(guibase.BaseInfoFrame):
    """Displays Past Battle Information"""  
    def __init__(self, mode, app, title='View Past Ship Battles'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(PastBattleInfoPanel(self))
        self.panel.populate()
            
class PastBattleInfoPanel(guibase.BasePanel):
    """Panel for viewing and sharing past ship Battles"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 4
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # choose a battle
        n = 0
        self.lbl = pyui.widgets.Label(text='CHOOSE SHIP BATTLE:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstBattles = pyui.widgets.ListBox(self.onBattleSelected, None, 100, 100, 0)
        self.addChild(self.lstBattles, (0, n+1, 4, 6+x))
        
        # fleets
        n = n+8+x
        self.lbl = pyui.widgets.Label(text='FLEETS IN BATTLE:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstFleets = pyui.widgets.ListBox(self.onFleetSelected, None, 100, 100, 0)
        self.addChild(self.lstFleets, (0, n+1, 4, 4+x))
        
        # ships
        n = n+6+x
        self.lbl = pyui.widgets.Label(text='SHIPS IN FLEET:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstShips = pyui.widgets.ListBox(self.onShipSelected, None, 100, 100, 0)
        self.addChild(self.lstShips, (0, n+1, 4, 4+x))
        self.btnShipInfo = pyui.widgets.Button('Ship Info', self.onShipInfo)
        self.addChild(self.btnShipInfo, (0, n+5+x, 2, 1))
        
        # share the battle?
        n = n+7+x
        self.lbl = pyui.widgets.Label(text='SHARE BATTLE:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstEmpires = pyui.widgets.ListBox(self.onEmpireSelected, None, 100, 100, 0)
        self.addChild(self.lstEmpires, (0, n+1, 4, 4+x))
        self.btnShareBattle = pyui.widgets.Button('Share Battle', self.onShareBattle)
        self.addChild(self.btnShareBattle, (0, n+5+x, 2, 1))
        self.btnViewBattle = pyui.widgets.Button('View Battle', self.onViewBattle)
        self.addChild(self.btnViewBattle, (0, n+6+x, 2, 1))
        
        # pack widgets
        self.pack
    
    def buildBattleData(self):
        """Display all available ship battle information"""
        return self.frame.mode.game.shipBattleDict

    def buildEmpireData(self):
        """Display Empires that battles can be shared with"""
        d = {}
        for empireID, myEmpireDict in self.frame.mode.game.allEmpires.iteritems():
            if empireID <> '1' and empireID <> self.frame.mode.game.myEmpireID:
                d[empireID] = '%s' % myEmpireDict['name']
        return d

    def buildFleetData(self):
        """Take current shipBattle object and display fleets from it"""
        d = {}
        for fleetID, myFleetDict in self.frame.mode.shipBattle.fleetsDict.iteritems():
            d[fleetID] = '%s - %d SHIPS (%s)' % (myFleetDict['name'], len(myFleetDict['ships'].keys()), self.frame.mode.game.allEmpires[myFleetDict['empireID']]['name'])
        return d
    
    def buildShipsInFleetData(self, fleetID):
        """Take Current shipBattle object and display all Ships contained within fleet"""
        d = {}
        myFleetDict = self.frame.mode.shipBattle.fleetsDict[fleetID]
        for shipID, myShipDict in myFleetDict['ships'].iteritems():
            d[shipID] = '%d:%s' % (myShipDict['position'], myShipDict['name'])
        return d
    
    def clearPanel(self):
        """Clear Panel Info"""
        # disable buttons, clear data
        self.btnShareBattle.disable()
        self.btnViewBattle.disable()
        self.btnShipInfo.disable()
        self.lstBattles.clear()
        self.lstFleets.clear()
        self.lstShips.clear()
        self.lstEmpires.clear()

    def onBattleSelected(self, item):
        """Select item from List"""
        if not item:
            self.populate()
        else:
            # ask server to update battle object and then populate fleet list
            self.frame.mode.getShipBattle(item.data)
            if self.frame.mode.shipBattle <> None:
                myFleets = self.buildFleetData()
                myEmpires = self.buildEmpireData()
                self.populateListbox(self.lstFleets, myFleets)
                self.populateListbox(self.lstEmpires, myEmpires)
                self.lstShips.clear()
                self.btnShareBattle.disable()
                self.btnViewBattle.enable()
  
    def onShipInfo(self, item):
        """Open Ship Info Panel"""
        fleetID = self.lstFleets.getSelectedItem().data
        shipID = self.lstShips.getSelectedItem().data
        myFleetDict = self.frame.mode.shipBattle.fleetsDict[fleetID]
        myShipDict = myFleetDict['ships'][shipID]
        myEmpireDict = self.frame.mode.shipBattle.empiresDict[myFleetDict['empireID']]
        myCaptainDict = self.frame.mode.shipBattle.captainsDict[myShipDict['captainID']]
        shipDesignDict = myEmpireDict['shipDesigns'][myShipDict['designID']]
        self.frame.mode.createShipInfoFrame(myShipDict, myFleetDict, myCaptainDict, 
                                            shipDesignDict, myEmpireDict)
    
    def onFleetSelected(self, item):
        """Select item from List"""
        if not item:
            self.populate()
        else:
            myShips = self.buildShipsInFleetData(item.data)
            self.populateListbox(self.lstShips, myShips)
    
    def onEmpireSelected(self, item):
        """Select item from List"""
        if not item:
            self.populate()
        else:
            self.btnShareBattle.enable()
    
    def onShareBattle(self, item):
        """Share Battle with Empire selected"""
        self.frame.mode.shareShipBattle(self.lstEmpires.getSelectedItem().data, self.lstBattles.getSelectedItem().data)
    
    def onViewBattle(self, item):
        """View Battle Selected"""
        self.frame.mode.viewShipBattle()
    
    def onShipSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnShipInfo.disable()
            self.frame.mode.destroyTempFrames()
        else:
            self.btnShipInfo.enable()
    
    def populate(self):
        """Populate frame with new data"""
        self.clearPanel()
        
        # load resources
        try:
            self.frame.mode.destroyTempFrames()
            myBattles = self.buildBattleData()
        except:
            # this allows for testing panel outside game
            myBattles = self.testDict
        
        # populate lists
        self.populateListbox(self.lstBattles, myBattles)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Past Battle Info Panel')
    app = run.TestApplication(width, height)
    frame = PastBattleInfoFrame(None, app)
    frame.panel.populate()
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
