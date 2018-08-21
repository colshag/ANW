# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# militaryinstinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all controls for Military Installation display and control
# This is brought up from the galactic map on a military installation click
# ---------------------------------------------------------------------------
import string

import pyui
import guibase
import anwp.func.funcs

class MilitaryInstInfoFrame(guibase.BaseInfoFrame):
    """Displays Military Installation Information"""  
    def __init__(self, mode, app, title='Military Installation Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(TabbedInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.militaryinstEntity = subject
        if self.militaryinstEntity.systemID <> self.currentID:
            # different MI populate panel
            self.currentID = self.militaryinstEntity.systemID
            self.setPanel(TabbedInfoPanel(self))
            self.panel.populate(self.militaryinstEntity.mySystemDict)

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the System"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.addPanel('BUILD', BuildInfoPanel(frame))
        self.addPanel('RESTORE', RestoreInfoPanel(frame))
        self.addPanel('UPGRADE', UpgradeInfoPanel(frame))
    
    def populate(self, mySystemDict):
        """When asked to populate the Panel will populate its sub panels"""
        self.mySystemDict = mySystemDict
        self.getPanel(0).populate(mySystemDict)
        self.getPanel(1).populate(mySystemDict)
        self.getPanel(2).populate(mySystemDict)
    
class BuildInfoPanel(guibase.BasePanel):
    """Panel for Building new Starships"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # MI info
        self.pctMI = pyui.widgets.Picture('')
        self.addChild(self.pctMI, (0, 0, 1, 3))
        self.lblName = pyui.widgets.Label(text=' Test Marines', type=1)
        self.addChild(self.lblName, (1, 0, 3, 1))
        self.lblMPAvail = pyui.widgets.Label(text=' Capacity (Used/Avail): 0/0', type=2)
        self.addChild(self.lblMPAvail, (1, 1, 3, 1))
        self.lblCadetsAvail = pyui.widgets.Label(text=' Marine Schools Avail: 0', type=2)
        self.addChild(self.lblCadetsAvail, (1, 2, 3, 1))
        
        # Choose design
        n = 4
        self.lbl = pyui.widgets.Label(text='CHOOSE REGIMENT TYPE:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstRegiment = pyui.widgets.ListBox(self.onRegimentSelected, None, 100, 100, 0)
        self.addChild(self.lstRegiment, (0, n+1, 4, 6+x))
        
        n = n+7+x
        self.buildResources(n, 'SELECTED REGIMENT COST:', 1, 'Regiment')
        
        # available resources
        n = n+4
        self.buildResources(n, 'AVAILABLE RESOURCES:', 1, 'Avail')
        
        n = n+4
        self.lbl = pyui.widgets.Label(text='BUILD:', type=1)
        self.addChild(self.lbl, (0, n, 1, 1))
        self.slbAmount = pyui.widgets.SliderBar(None, 50)
        self.addChild(self.slbAmount, (1, n, 2, 1))
        self.btnBuild = pyui.widgets.Button('Build', self.onBuildRegiment)
        self.addChild(self.btnBuild, (3, n, 1, 1))
        
        n = n+2
        self.buildOrders(n,x,'CURRENT INSTALLATION ORDERS:',5)
        
        # pack widgets
        self.pack
    
    def buildRegimentData(self):
        """Display all available Regiment Types"""
        d = {}
        for dataID in self.frame.mode.game.myEmpire['researchedRegiments']:
            abr = self.frame.mode.game.regimentdata[dataID]['abr']
            if abr[1:] <> 'ML':
                name = self.frame.mode.game.regimentdata[dataID]['name']
                d[dataID] = name
        return d
    
    def buildOrderData(self, dIndOrderData):
        """Display all MI orders this round"""
        d = {}
        for id, dIndOrder in dIndOrderData.iteritems():
            if dIndOrder['system'] == self.mySystemDict['id'] and dIndOrder['type'] == 'Add Regiment':
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                (amount, regimentType) = string.split(dIndOrder['value'], '-')
                name = 'ADD %s: %s' % (amount, self.frame.mode.game.regimentdata[regimentType]['name'])
                d[id] = name
        return d
    
    def enableBuildRegiment(self):
        """Check if MI should allow regiments to be built"""
        myRegimentDict = self.frame.mode.game.regimentdata[self.lstRegiment.getSelectedItem().data]
        # check if regiment could be built
        amount = int(self.slbAmount.position)
        if (self.myEmpireDict['CR'] >= myRegimentDict['costCR'] * amount and
            self.mySystemDict['AL'] >= myRegimentDict['costAL'] * amount and
            self.mySystemDict['EC'] >= myRegimentDict['costEC'] * amount and
            self.mySystemDict['IA'] >= myRegimentDict['costIA'] * amount and
            (self.mySystemDict['availMIC'] - self.mySystemDict['usedMIC']) >= (100*amount)
            and amount > 0):
            self.btnBuild.enable()
        else:
            self.btnBuild.disable()
    
    def onBuildRegiment(self, item):
        """Send a Build Regiment command to server"""
        self.frame.mode.addRegimentOrder(self.slbAmount.position, self.lstRegiment.getSelectedItem().data, self.mySystemDict['id'])

    def onRegimentSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnBuild.disable()
        else:
            # create temporary design for display
            myRegimentDict = self.frame.mode.game.regimentdata[item.data]
            self.lblTotalCRRegiment.setText('%d' % myRegimentDict['costCR'])
            self.lblTotalALRegiment.setText('%d' % myRegimentDict['costAL'])
            self.lblTotalECRegiment.setText('%d' % myRegimentDict['costEC'])
            self.lblTotalIARegiment.setText('%d' % myRegimentDict['costIA'])
            self.enableBuildRegiment()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def populate(self, mySystemDict):
        """Populate frame with new data"""
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnBuild.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            self.myEmpireDict = self.frame.mode.game.myEmpire
            name = 'militaryinst_%s_%s' % (self.frame.mode.game.myEmpire['color1'], self.frame.mode.game.myEmpire['color2'])
            myPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myRegiments = self.buildRegimentData()
            myOrders = self.buildOrderData(self.myEmpireDict['industryOrders'])
            self.lblName.setText(' %s Marines' % mySystemDict['name'])
            self.lblMPAvail.setText(' Capacity: %d/%d' % (mySystemDict['usedMIC'], mySystemDict['availMIC']))
            self.lblCadetsAvail.setText(' Marine Cadet Classes: %d' % self.mySystemDict['armyCadets'])
            self.lblTotalCRAvail.setText('%d' % self.myEmpireDict['CR'])
            self.lblTotalALAvail.setText('%d' % self.mySystemDict['AL'])
            self.lblTotalECAvail.setText('%d' % self.mySystemDict['EC'])
            self.lblTotalIAAvail.setText('%d' % self.mySystemDict['IA'])
        except:
            # this allows for testing panel outside game
            myPict = self.testImagePath + 'empire1.png'
            myRegiments = myOrders = self.testDict
        
        # Military Inst info        
        self.pctMI.setFilename(myPict)
        self.populateListbox(self.lstRegiment, myRegiments)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)

class RestoreInfoPanel(guibase.BasePanel):
    """Panel for Restoring Marine Regiments"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # MI info
        self.pctMI = pyui.widgets.Picture('')
        self.addChild(self.pctMI, (0, 0, 1, 3))
        self.lblName = pyui.widgets.Label(text=' Test Marines', type=1)
        self.addChild(self.lblName, (1, 0, 3, 1))
        self.lblMPAvail = pyui.widgets.Label(text=' Capacity (Used/Avail): 0/0', type=2)
        self.addChild(self.lblMPAvail, (1, 1, 3, 1))
        
        # Choose Regiment to Restore
        n = 3
        self.lblA = pyui.widgets.Label(text='CHOOSE REGIMENTS TO RESTORE:', type=1)
        self.addChild(self.lblA, (0, n, 4, 1))
        self.lstRegiment = pyui.widgets.ListBox(self.onRegimentSelected, None, 100, 100, 1)
        self.addChild(self.lstRegiment, (0, n+1, 4, 6+x))
        self.btnAllRegiments = pyui.widgets.Button('Select All Regiments', self.onAllRegiments)
        self.addChild(self.btnAllRegiments, (0, n+7+x, 4, 1))
        
        n = n+9+x
        self.lblB = pyui.widgets.Label(text='TOTAL RESTORE COST:', type=1)
        self.addChild(self.lblB, (0,n,4,1))
        n = n+1
        self.buildResources(n, '', 1, 'Regiment')
        
        # available resources
        n = n+3
        self.buildResources(n, 'AVAILABLE RESOURCES:', 1, 'Avail')
        
        n = n+3
        self.btnRestore = pyui.widgets.Button('Restore Selected Regiments', self.onRestoreRegiment)
        self.addChild(self.btnRestore, (0, n, 4, 1))
        
        n = n+2
        self.buildOrders(n,x,'CURRENT INSTALLATION ORDERS:',5)
        
        # pack widgets
        self.pack
    
    def buildRegimentData(self):
        """Display all Regiments in need of some restoration"""
        d = {}
        for myRegimentID, myRegimentDict in self.frame.mode.game.myRegiments.iteritems():
            if (myRegimentDict['state'] == 1 
                and myRegimentDict['fromSystem'] == self.mySystemDict['id']
                and myRegimentDict['strength'] < 100
                and myRegimentID not in self.toRestoreRegiments):
                d['%s' % myRegimentID] = '%s(%d%s)' % (myRegimentDict['name'], myRegimentDict['strength'], '%')
        return d
    
    def buildOrderData(self, dIndOrderData):
        """Display all MI orders this round"""
        d = {}
        self.toRestoreRegiments = [] # list of regiments being restored
        for id, dIndOrder in dIndOrderData.iteritems():
            if dIndOrder['system'] == self.mySystemDict['id'] and dIndOrder['type'] =='Restore Regiment':
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                name = ''
                if dIndOrder['type'] == 'Restore Regiment':
                    myRegimentDict = self.getMyRegimentDict(dIndOrder['value'])
                    name = 'RES %s(%d%s)' % (myRegimentDict['name'], myRegimentDict['strength'], '%')
                    self.toRestoreRegiments.append(myRegimentDict['id'])
                if name <> '':
                    d[id] = name
        return d
    
    def enableRestoreRegiment(self):
        """Check if MI should allow Regiment to be restored"""
        myRegimentDict = self.getMyRegimentDict()
        # check if Regiment can be restored
        [CR,AL,EC,IA,capacity] = self.getRestorationCost()
        if (self.myEmpireDict['CR'] >= CR and
            self.mySystemDict['AL'] >= AL and
            self.mySystemDict['EC'] >= EC and
            self.mySystemDict['IA'] >= IA and
            (self.mySystemDict['availMIC'] - self.mySystemDict['usedMIC']) >= capacity):
            self.btnRestore.enable()
        else:
            self.btnRestore.disable()
    
    def getRestorationCost(self):
        """Return the Restoration Cost of selected Regiments"""
        CR = 0
        AL = 0
        EC = 0
        IA = 0
        capacity = 0
        for item in self.lstRegiment.getMultiSelectedItems():
            myRegimentDict = self.getMyRegimentDict(item)
            CR += myRegimentDict['restoreCost'][0]
            AL += myRegimentDict['restoreCost'][1]
            EC += myRegimentDict['restoreCost'][2]
            IA += myRegimentDict['restoreCost'][3]
            capacity += (100 - myRegimentDict['strength'])
        return [CR,AL,EC,IA,capacity]
    
    def getMyRegimentDict(self, value=''):
        """Return the Regiment Dict of selected Regiment"""
        if value == '':
            value = self.lstRegiment.getSelectedItem().data
        
        myRegimentDict = self.frame.mode.game.myRegiments[value]
        return myRegimentDict
    
    def onAllRegiments(self, item):
        """Select All Regiments"""
        for key in self.lstRegiment.dSelected.keys():
            self.lstRegiment.dSelected[key] = 1
        self.lstRegiment.setDirty()
        self.enableRestoreRegiment()
    
    def onRestoreRegiment(self, item):
        """Send a Restore Regiment Command to server"""
        self.frame.mode.restoreRegimentOrder(self.lstRegiment.getMultiSelectedItems(), self.mySystemDict['id'])

    def onRegimentSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnRestore.disable()
        else:
            [CR,AL,EC,IA,capacity] = self.getRestorationCost()
            self.lblTotalCRRegiment.setText('%d' % CR)
            self.lblTotalALRegiment.setText('%d' % AL)
            self.lblTotalECRegiment.setText('%d' % EC)
            self.lblTotalIARegiment.setText('%d' % IA)
            self.enableRestoreRegiment()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def populate(self, mySystemDict):
        """Populate frame with new data"""
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnRestore.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            self.myEmpireDict = self.frame.mode.game.myEmpire
            name = 'militaryinst_%s_%s' % (self.frame.mode.game.myEmpire['color1'], self.frame.mode.game.myEmpire['color2'])
            myPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myOrders = self.buildOrderData(self.myEmpireDict['industryOrders'])
            myRegiments = self.buildRegimentData()
            self.lblName.setText(' %s Marines' % mySystemDict['name'])
            self.lblMPAvail.setText(' Capacity: %d/%d' % (mySystemDict['usedMIC'], mySystemDict['availMIC']))
            self.lblTotalCRAvail.setText('%d' % self.myEmpireDict['CR'])
            self.lblTotalALAvail.setText('%d' % self.mySystemDict['AL'])
            self.lblTotalECAvail.setText('%d' % self.mySystemDict['EC'])
            self.lblTotalIAAvail.setText('%d' % self.mySystemDict['IA'])
        except:
            # this allows for testing panel outside game
            myPict = self.testImagePath + 'empire1.png'
            myRegiments = myOrders = self.testDict
        
        # Military Inst info        
        self.pctMI.setFilename(myPict)
        self.populateListbox(self.lstRegiment, myRegiments)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)
        
class UpgradeInfoPanel(RestoreInfoPanel):
    """Panel for Upgrading Regiments"""
    def __init__(self, frame):
        RestoreInfoPanel.__init__(self, frame)
        self.lblA.setText('CHOOSE REGIMENTS TO UPGRADE:')
        self.lblB.setText('TOTAL UPGRADE COST:')
        self.btnRestore.setText('Upgrade Selected Regiments')

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Military Installation Info Panel')
    app = run.TestApplication(width, height)
    frame = MilitaryInstInfoFrame(None, app)
    frame.panel.populate(None)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
