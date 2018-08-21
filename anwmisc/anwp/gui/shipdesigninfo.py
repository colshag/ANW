# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipdesigninfo.py.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Allows a player to create a ship design in the shipdesign mode
# ---------------------------------------------------------------------------
import string

import pyui
import guibase
import anwp.func.globals

class ShipDesignInfoFrame(guibase.BaseInfoFrame):
    """Displays Ship Design Information"""  
    def __init__(self, mode, app, myDesign, title='Ship Design'):
        self.myDesign = myDesign
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(TabbedInfoPanel(self))
        self.panel.populate(myDesign)

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the Ship Design"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.frame = frame
        self.addPanel('GENERAL', GeneralInfoPanel(frame))
        self.addPanel('WEAPON', AddWeaponPanel(frame))
        self.addPanel('COMPONENT', AddComponentPanel(frame))
    
    def populate(self, myDesign):
        """When asked to populate the Panel will populate its sub panels"""
        self.frame.myDesign = myDesign
        self.getPanel(0).populate()
        self.getPanel(1).populate()
        self.getPanel(2).populate()
    
class GeneralInfoPanel(guibase.BasePanel):
    """Panel for adding ship hull and general design information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # choose hull
        self.lbl = pyui.widgets.Label('CHOOSE A SHIP HULL:', type=1)
        self.addChild(self.lbl, (0,0,4,1))
        self.lstShipHulls = pyui.widgets.ListBox(self.onShipHullSelected, None, 100, 100, 0)
        self.addChild(self.lstShipHulls, (0,1,4,3+x))
        self.btnSwitchHull = pyui.widgets.Button('Switch Hull', self.onSwitchHull)
        self.addChild(self.btnSwitchHull, (0,4+x,2,1))
        
        n = 5+x
        self.lblHullName = pyui.widgets.Label('Hull: Interceptor', type=2)
        self.addChild(self.lblHullName, (0,n,4,1))
        self.pctShipHull = pyui.widgets.Picture('')
        self.addChild(self.pctShipHull, (0,n+1,1,3))
        self.pctHullType = pyui.widgets.Picture('')
        self.addChild(self.pctHullType, (1,n+1,3,3))
        
        n = n+5
        self.buildResources(n,'SHIP HULL STATS:', 1, 'Hull')
        
        n = n+3
        self.lblMaxComps = pyui.widgets.Label(text='Total Components: 8')
        self.addChild(self.lblMaxComps, (0,n,4,1))
        self.lblMaxISP = pyui.widgets.Label(text='Hull ISP: 1000')
        self.addChild(self.lblMaxISP, (0,n+1,4,1))
        
        # choose design name
        n = n+2
        self.lbl = pyui.widgets.Label('DESIGN NAME:', type=1)
        self.addChild(self.lbl, (0,n,2,1))
        self.txtDesignName = pyui.widgets.Edit('', 20)
        self.addChild(self.txtDesignName, (0,n+1,4,1))
        
        n = n+3
        self.buildResources(n, 'TOTAL SHIP COST:', 1, 'Design')
        
        n = n+3
        self.lblDesignsLeft = pyui.widgets.Label('Designs Left this Round: 2', type=2)
        self.addChild(self.lblDesignsLeft, (0,n,4,1))
        self.btnSaveDesign = pyui.widgets.Button('Submit Design', self.onSubmitDesign)
        self.addChild(self.btnSaveDesign, (0,n+1,2,1))
        self.btnClearDesign = pyui.widgets.Button('Clear Design', self.onClearDesign)
        self.addChild(self.btnClearDesign, (2,n+1,2,1))

        # current designs
        n = n+3
        self.lbl = pyui.widgets.Label('CURRENT DESIGNS:', type=1)
        self.addChild(self.lbl, (0,n,2,1))
        self.lstCurrentDesigns = pyui.widgets.ListBox(self.onCurrentDesignSelected, None, 100, 100, 0)
        self.addChild(self.lstCurrentDesigns, (0,n+1,4,2+x))
        self.btnRemoveDesign = pyui.widgets.Button('Remove Design', self.onRemoveDesign)
        self.addChild(self.btnRemoveDesign, (0,n+3+x,2,1))

        # pack widgets
        self.pack

    def buildShipDesigns(self):
        """format what ship designs have currently been created"""
        d = {}
        shipDesignList = self.frame.mode.game.shipDesigns.keys()
        shipDesignList.sort()
        for shipDesignID in shipDesignList:
            myShipDesignTuple = self.frame.mode.game.shipDesigns[shipDesignID]
            d[shipDesignID] = '%s' % (myShipDesignTuple[0])
        return d
    
    def onClearDesign(self, item):
        """Clear all Design Decisions"""
        self.txtDesignName.setText('')
        self.frame.mode.resetDesign()
        
    def onCurrentDesignSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnRemoveDesign.disable()
        else:
            selected = self.lstCurrentDesigns.selected
            name = self.lstCurrentDesigns.getSelectedItem().name
            (designName, shipHullID, compDict, weapDict) = self.frame.mode.game.shipDesigns[self.lstCurrentDesigns.items[selected].data]
            self.frame.mode.resetDesign(shipHullID)
            self.frame.mode.myShipDesign = self.frame.mode.getShipDesign(shipHullID, compDict, weapDict)
            self.frame.mode.refreshPanels(1)
            self.btnRemoveDesign.enable()
            self.lstCurrentDesigns.setSelectedItem(name)
            self.frame.title = designName
    
    def onShipHullSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnSwitchHull.disable()
        else:
            self.btnSwitchHull.enable()

    def onRemoveDesign(self, item):
        """Remove selected Design"""
        self.frame.mode.removeShipDesign(self.lstCurrentDesigns.getSelectedItem().data)
        self.onClearDesign(None)
            
    def onSwitchHull(self, item):
        """Switch current Hull with new Hull selected"""
        self.frame.mode.resetDesign(self.lstShipHulls.getSelectedItem().data)
    
    def onSubmitDesign(self, item):
        """Submit Design to Server"""
        self.frame.mode.submitDesign(self.txtDesignName.text)
        self.frame.mode.resetDesign()
    
    def populate(self):
        """Populate frame with new data"""
        # disable buttons
        self.btnSwitchHull.disable()
        self.btnRemoveDesign.disable()
        
        # load resources
        myDesign = self.frame.myDesign
        myHull = myDesign.myShipHull
        try:
            color1 = self.frame.mode.game.myEmpire['color1']
            color2 = self.frame.mode.game.myEmpire['color2']
            name = '%sb_%s_%s' % (string.lower(myHull.abr), color1, color2)
            myShipHullPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myShipHullTypePict = '%s%s.png' % (self.frame.app.genImagePath, myHull.function)
            myShipHulls = self.buildAvail(self.frame.mode.game.shiphulldata)
            designsLeft = self.frame.mode.game.myEmpire['designsLeft']
            myShipDesigns = self.buildShipDesigns()
        except:
            # this allows for testing panel outside game
            myShipHullPict = self.testImagePath + 'sctb.png'
            myShipHullTypePict = self.testImagePath + 'warship.png'
            myShipHulls = self.testDict
            myShipDesigns = self.testDict
            designsLeft = 888
        
        # ship hulls
        self.populateListbox(self.lstShipHulls, myShipHulls)
        
        # hull info
        self.lblHullName.setText('Hull: %s' % myHull.name)
        self.pctShipHull.setFilename(myShipHullPict)
        self.pctHullType.setFilename(myShipHullTypePict)
        self.lblMaxComps.setText('Total Components: %d' % (myHull.componentNum*4))
        self.lblMaxISP.setText('Hull ISP: %s' % myHull.maxISP)
        
        # Ship Hull Cost
        self.lblTotalCRHull.setText('%d' % (myHull.costCR))
        self.lblTotalALHull.setText('%d' % (myHull.costAL))
        self.lblTotalECHull.setText('%d' % (myHull.costEC))
        self.lblTotalIAHull.setText('%d' % (myHull.costIA))
        
        # Total Design Cost
        self.lblTotalCRDesign.setText('%d' % (myDesign.costCR))
        self.lblTotalALDesign.setText('%d' % (myDesign.costAL))
        self.lblTotalECDesign.setText('%d' % (myDesign.costEC))
        self.lblTotalIADesign.setText('%d' % (myDesign.costIA))
        
        self.lblDesignsLeft.setText('Designs Left this Round: %s' % designsLeft)
        self.populateListbox(self.lstCurrentDesigns, myShipDesigns)

class AddWeaponPanel(guibase.BasePanel):
    """Panel for adding weapons to Ship Design"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 1
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # choose from available weapons
        self.lblTitle = pyui.widgets.Label('', type=1)
        self.addChild(self.lblTitle, (0,0,4,1))
        self.setTitle()
        self.lstAdd = pyui.widgets.ListBox(self.onSelected, None, 100, 100, 0)
        self.addChild(self.lstAdd, (0,1,4,3+x))
        
        n = 4+x
        self.addEndData(n)
        
        n = n+5
        self.pctMain = pyui.widgets.Picture('')
        self.addChild(self.pctMain, (0,n,1,3))
        self.pctType = pyui.widgets.Picture('')
        self.addChild(self.pctType, (1,n,3,3))
                
        n = n+3
        self.setMyStats(n)
        
        n = n+14
        self.buildResources(n,'',1)
        
        # pack widgets
        self.pack

    def addEndData(self, n):
        """Add the end panel data"""
        # choose a quad to add to
        self.lbl = pyui.widgets.Label('QUADRANT:', type=1)
        self.addChild(self.lbl, (0,n,2,1))
        self.lbl = pyui.widgets.Label('WEAPON FACING:', type=1)
        self.addChild(self.lbl, (2,n,2,1))
        self.lstQuad = pyui.widgets.ListBox(self.onQuadSelected, None, 100, 100, 0)
        self.addChild(self.lstQuad, (0,n+1,2,3))
        self.lstFacing = pyui.widgets.ListBox(self.onFacingSelected, None, 100, 100, 0)
        self.addChild(self.lstFacing, (2,n+1,2,3))
        d = {'fore':'FORE', 'aft':'AFT', 'port':'PORT', 'star':'STAR'}
        self.populateListbox(self.lstQuad, d)
        self.populateListbox(self.lstFacing, d)
        self.btnAdd = pyui.widgets.Button('Add Weapon', self.onAdd)
        self.addChild(self.btnAdd, (0,n+4,2,1))
        self.btnAdd.disable()
        self.txtFacing = pyui.widgets.NumberEdit('', 3, None, 0)
        self.addChild(self.txtFacing, (2,n+4,2,1))

    def clearData(self):
        """Clear all data if nothing is selected"""
        # pictures
        self.pctMain.setFilename('')
        self.pctType.setFilename('')
        
        # attributes
        i = 0
        while i <= self.statNum:
            myLabel = getattr(self, 'lbl%d' % i)
            myLabel.setText('')
            i += 1
        
        # resources
        for item in ['CR','AL','EC','IA']:
            myLabel = getattr(self, 'lblTotal%s' % item)
            myLabel.setText('0')

    def onAdd(self, item):
        """On Add item button pressed"""
        # store names so listboxes can be reset to same positions
        addName = self.lstAdd.getSelectedItem().name
        quadName = self.lstQuad.getSelectedItem().name
        
        type = self.lstAdd.getSelectedItem().data
        quad = self.lstQuad.getSelectedItem().data
        if self.btnAdd.text == 'Add Component':
            result = self.frame.myDesign.addComponent(type, quad)
        else:
            ##TODO: drone design portion commented with '' for now
            result = self.frame.myDesign.addWeapon(type, quad, self.txtFacing.getValue(), '')
        if result <> 1:
            self.frame.mode.modeMsgBox(result)
        else:
            self.frame.mode.updateDesign()
            # reset listboxes to old positions
            self.lstAdd.setSelectedItem(addName)
            self.lstQuad.setSelectedItem(quadName)
            self.onSelected(item)

    def onFacingSelected(self, item):
        """On item selected"""
        if not item:
            pass
        else:
            self.txtFacing.setText(str(anwp.func.globals.quadAngles[item.data]))

    def onSelected(self, item):
        """On item selected"""
        if not item:
            self.btnAdd.disable()
        else:
            self.clearData()
            # populate panel with data
            myWeapon = self.frame.mode.game.weapondata[self.lstAdd.getSelectedItem().data]
            dataList = ['range','arc','maxPower','damage','speed','tracking','maxLock',
                        'maxCompHP','numComps','ammo','AMS','missile','direct','drone']
            self.populateData(myWeapon, dataList)
    
    def onQuadSelected(self, item):
        """On Quadrant item selected, only enable add button if an item is selected"""
        if not item:
            self.btnAdd.disable()
        elif self.lstAdd.selected < self.lstAdd.numItems and self.lstAdd.selected <> -1:
            self.btnAdd.enable()
    
    def populate(self):
        """Populate frame with new data"""
        # disable buttons, clear data
        self.clearData()
        
        # load weapons available
        try:
            myAvail = self.buildAvail(self.frame.mode.game.weapondata)
        except:
            myAvail = self.testDict
            
        self.populateListbox(self.lstAdd, myAvail)
    
    def populateData(self, myObj, dataList):
        """Populate Panel with data from selected item"""
        # set pictures
        main = string.lower(myObj.abr[0])
        type = string.lower(myObj.abr[1:3])
        self.pctMain.setFilename('%s%s.png' % (self.frame.app.genImagePath, main))
        self.pctType.setFilename('%s%s.png' % (self.frame.app.genImagePath, type))
        
        # set attributes
        i = 0
        for item in dataList:
            myLabel = getattr(self, 'lbl%d' % i)
            myValue = getattr(myObj, item)
            myLabel.setText(str(myValue))
            i += 1
        
        # set cost
        for item in ['CR','AL','EC','IA']:
            myLabel = getattr(self, 'lblTotal%s' % item)
            myValue = getattr(myObj, 'cost%s' % item)
            myLabel.setText(str(myValue))
    
    def setMyStats(self, n):
        """Set specific to this panel stats"""
        attrList = ['Range:', 'Arc:', 'Power Req:', 'Damage:', 'Speed:', 'Tracking:', 'Lock:',
                     'maxCompHP:', 'numComps:', 'Ammo:', 'AMS:', 'Missile:', 'Direct:', 'Drone:']
        self.setStats(n, attrList)
    
    def setTitle(self):
        """Set the title of this panel"""
        self.lblTitle.setText('CHOOSE A WEAPON TO ADD:')
    
class AddComponentPanel(AddWeaponPanel):
    """Panel for adding components to Ship Design"""
    def __init__(self, frame):
        AddWeaponPanel.__init__(self, frame)
    
    def addEndData(self, n):
        """Add the end panel data"""
        # choose a quad to add to
        self.lbl = pyui.widgets.Label('CHOOSE A QUADRANT:', type=1)
        self.addChild(self.lbl, (0,n,4,1))
        self.lstQuad = pyui.widgets.ListBox(self.onQuadSelected, None, 100, 100, 0)
        self.addChild(self.lstQuad, (0,n+1,4,3))
        d = {'fore':'Fore', 'aft':'Aft', 'port':'Port', 'star':'Starboard'}
        self.populateListbox(self.lstQuad, d)
        self.btnAdd = pyui.widgets.Button('Add Weapon', self.onAdd)
        self.addChild(self.btnAdd, (0,n+4,2,1))
        self.btnAdd.disable()
        
    def populate(self):
        """Populate frame with new data"""
        # disable buttons, clear data
        self.clearData()
        
        # load weapons available
        try:
            myAvail = self.buildAvail(self.frame.mode.game.componentdata)
        except:
            myAvail = self.testDict
            
        self.populateListbox(self.lstAdd, myAvail)
        self.btnAdd.setText('Add Component')
        
    def onSelected(self, item):
        """On item selected"""
        if not item:
            self.btnAdd.disable()
        else:
            self.clearData()
            # populate panel with data
            myComponent = self.frame.mode.game.componentdata[self.lstAdd.getSelectedItem().data]
            dataList = ['maxAmmo','storage','engine','rotate','power','battery','repair',
                        'target','radar','genSP','maxSP','maxAP','maxHP']
            self.populateData(myComponent, dataList)
        
    def setMyStats(self, n):
        """Set specific to this panel stats"""
        attrList = ['MaxAmmo:','Storage:','Engines:','Rotates:','Power:','Battery:','Repair:',
                    'Targetting:','Radar:','Shield Gen:','Shields:','Armor:','CompHP:']
        self.setStats(n, attrList)
    
    def setTitle(self):
        """Set the title of this panel"""
        self.lblTitle.setText('CHOOSE A COMPONENT TO ADD:')
    
def main():
    """Run gui for testing"""
    import run
    import anwp.func.storedata
    width = 1024
    height = 768
    myGalaxy = anwp.func.storedata.loadFromFile('../../../Database/ANW1.anw')
    myEmpire = myGalaxy.empires['1']
    myDesign = myEmpire.shipDesigns['1']
    pyui.init(width, height, 'p3d', 0, 'Testing Ship Design Panel')
    app = run.TestApplication(width, height)
    frame = ShipDesignInfoFrame(None, app, myDesign)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
