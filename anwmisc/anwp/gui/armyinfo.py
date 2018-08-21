# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# aarmyinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all controls for an army of regiments on the galactic map
# ---------------------------------------------------------------------------
import types
import string

import pyui
import guibase
import anwp.func.funcs
import anwp.func.globals

class ArmyInfoFrame(guibase.BaseInfoFrame):
    """Displays Armada Information"""  
    def __init__(self, mode, app, title='Army Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(ArmyInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.armyEntity = subject
        if self.armyEntity.systemID <> self.currentID:
            # different army populate panel
            self.currentID = self.armyEntity.systemID
            
            # check if Army owned by player
            if self.armyEntity.myEmpireDict['id'] == self.mode.game.myEmpireID:
                self.setPanel(ArmyInfoPanel(self))
            else:
                self.setPanel(OtherArmyInfoPanel(self))
            
            # populate panel
            self.panel.populate(self.armyEntity.myEmpireDict, self.armyEntity.mySystemDict)
            
class ArmyInfoPanel(guibase.BasePanel):
    """Panel for commanding Armies"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 4
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # choose a regiment
        n = 0
        self.lbl = pyui.widgets.Label(text='CHOOSE AN REGIMENT:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstRegiments = pyui.widgets.ListBox(self.onRegimentSelected, None, 100, 100, 1)
        self.addChild(self.lstRegiments, (0, n+1, 4, 15+x))
        self.btnAllRegiments = pyui.widgets.Button('Select All', self.onAllRegiments)
        self.addChild(self.btnAllRegiments, (2, n+16+x, 2, 1))
        self.btnRegimentInfo = pyui.widgets.Button('Regiment Info', self.onRegimentInfo)
        self.addChild(self.btnRegimentInfo, (0, n+16+x, 2, 1))
        
        # view regiment details
        n = n+18+x
        self.lbl = pyui.widgets.Label(text='SELECTED REGIMENT ORDERS:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lblCurrentOrder = pyui.widgets.Label('', type=2)
        self.addChild(self.lblCurrentOrder, (0, n+1, 4, 1))
        
        # give regiment new orders
        n = n+3
        self.lbl = pyui.widgets.Label(text='GIVE REGIMENT NEW ORDERS:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstOrders = pyui.widgets.ListBox(self.onOrderSelected, None, 100, 100, 0)
        self.addChild(self.lstOrders, (0, n+1, 4, 5+x))
        self.btnNewOrder = pyui.widgets.Button('Submit New Order', self.onNewOrder)
        self.addChild(self.btnNewOrder, (0, n+6+x, 4, 1))
        
        # pack widgets
        self.pack
    
    def buildRegimentData(self):
        """Display all player regiments in Army"""
        d = {}
        regimentsAtSystem = self.frame.mode.game.myArmies[self.mySystemDict['id']]
        regimentsAtSystem = anwp.func.funcs.sortStringList(regimentsAtSystem)
        num = 0
        for id in regimentsAtSystem:
            myRegimentDict = self.frame.mode.game.myRegiments[id]
            if myRegimentDict['state'] in [1,4]:
                location = self.mySystemDict['name']
                if myRegimentDict['state'] == 1:
                    num = 1
            else:
                location = self.frame.mode.game.myFleets[myRegimentDict['fromShip']]['name']
            d[id] = '%s -> %s' % (myRegimentDict['name'], location)

        return d
        
    def buildOrdersAvailableData(self, regimentID):
        """Display all orders available to Regiment"""
        d = {}
        myRegimentDict = self.frame.mode.game.myRegiments[regimentID]
        systemID = myRegimentDict['unloadToSystem']
        if systemID <> '':
            d[systemID] = 'UNLOAD->%s' % self.frame.mode.game.allSystems[systemID]['name']
        for item in myRegimentDict['loadToShips']:
            myShipData = self.frame.mode.game.myFleets[myRegimentDict['fromShip']]
            d[item] = 'LOAD->%s(%s/%s)' % (myShipData['name'], myShipData['currentTransport'], myShipData['maxTransport'])
        return d
    
    def clearPanel(self):
        """Clear Panel Info"""
        # disable buttons, clear data
        self.btnRegimentInfo.disable()
        self.btnNewOrder.disable()
        self.lstRegiments.clear()
        self.lstOrders.clear()
        self.lblCurrentOrder.setText('')
    
    def onAllRegiments(self, item):
        """Select All Regiments from List"""
        for key in self.lstRegiments.dSelected.keys():
            self.lstRegiments.dSelected[key] = 1
        self.lstRegiments.setDirty()
        self.onRegimentSelected(item)
    
    def onNewOrder(self, item):
        """Set new Orders for Regiment"""
        list = self.lstRegiments.getMultiSelectedItems()
        self.frame.mode.setRegimentOrder(list, self.lstOrders.getSelectedItem().data)
        
    def onRegimentInfo(self, item):
        """display regiment info"""
        regimentID = self.lstRegiments.getSelectedItem().data
        myRegimentDict = self.frame.mode.game.myRegiments[regimentID]
        self.frame.mode.modeMsgBox('%s -> STATE: %s - GLORY: %d Victories' % 
                                   (myRegimentDict['name'], anwp.func.globals.regimentStates[myRegimentDict['state']], myRegimentDict['glory']))
    
    def onRegimentSelected(self, item):
        """Select item from List"""
        regimentList = self.lstRegiments.getMultiSelectedItems()
        sameState = 1
        currentState = 0
        for regimentID in regimentList:
            myRegimentDict = self.frame.mode.game.myRegiments[regimentID]
            myState = myRegimentDict['state']
            if currentState == 0:
                currentState = myState
            if myState <> currentState:
                sameState = 0
        
        if self.lstRegiments.getMultiSelectedItems() == [] or sameState == 0:
            self.populate(self.myEmpireDict, self.mySystemDict)
            if sameState == 0:
                self.frame.mode.modeMsgBox('Selection Cleared: you cannot give orders to Regiments in different States')
        else:
            # display current regiment status
            self.btnCreateRegiment.disable()
            regimentID = regimentList[0]
            myRegimentDict = self.frame.mode.game.myRegiments[regimentID]
            myState = myRegimentDict['state']
            if myState == 1:
                name = self.frame.mode.game.allSystems[myRegimentDict['fromSystem']]['name']
                self.btnCreateRegiment.enable()
            elif myState in [2,3]:
                name = self.frame.mode.game.myFleets[myRegimentDict['fromShip']]['name']
            elif myState == 4:
                name = self.frame.mode.game.allSystems[myRegimentDict['toSystem']]['name']
            self.lblCurrentOrder.setText('%s->%s' % (anwp.func.globals.regimentStates[myState],name))
            
            # display other regiment options
            myOrders = self.buildOrdersAvailableData(regimentID)
            self.populateListbox(self.lstOrders, myOrders)
            
            # do not display information if more then one regiment selected
            if len(regimentList) == 1:
                self.btnRegimentInfo.enable()
            else:
                self.btnRegimentInfo.disable()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnNewOrder.disable()
        else:
            self.enableButtons(self.lstRegiments, [self.btnNewOrder])
    
    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        self.clearPanel()
        
        # load resources
        try:
            self.frame.mode.destroyTempFrames()
            myRegiments = self.buildRegimentData()
            self.frame.title = '%s: Regiment Information' % mySystemDict['name']
        except:
            # this allows for testing panel outside game
            myRegiments = self.testDict
        
        # populate lists
        self.populateListbox(self.lstRegiments, myRegiments)

class OtherArmyInfoPanel(guibase.BasePanel):
    """Panel for Viewing other Armies"""
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
        self.lblOwnedBy = pyui.widgets.Label(text='  Army Owned By:', type=2)
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
            self.frame.title = '%s: Army Information' % mySystemDict['name']
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
    pyui.init(width, height, 'p3d', 0, 'Testing Army Info Panel')
    app = run.TestApplication(width, height)
    frame = ArmyInfoFrame(None, app)
    frame.panel.populate(None,None)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
