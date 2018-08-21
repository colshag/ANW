# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# quadinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all the components and some other ship quad info
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals
import anwp.func.funcs

class QuadInfoFrame(guibase.BaseFrame):
    """Displays Quad Information"""  
    def __init__(self, mode, app, quad, x, y, w, h):
        self.mode = mode
        self.app = app
        self.quad = quad
        # load data
        try:
            self.componentdata = self.mode.game.componentdata
            self.weapondata = self.mode.game.weapondata
            self.shiphulldata = self.mode.game.shiphulldata
        except:
            # this is running in test mode, load data direct from object
            self.componentdata = self.quad.myParent.myGalaxy.componentdata
            self.weapondata = self.quad.myParent.myGalaxy.weapondata
            self.shiphulldata = self.quad.myParent.myGalaxy.shiphulldata
        title = quad.position
        guibase.BaseFrame.__init__(self, mode, x, y, w, h, title)
        self.setPanel(TabbedInfoPanel(self))
        self.panel.populate(quad)

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the Quad"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.frame = frame
        self.addPanel('Components', ComponentsInfoPanel(frame))
        self.addPanel('Weapons', WeaponsInfoPanel(frame))
        
    def populate(self, quad):
        """When asked to populate the Panel will populate the active panel"""
        self.frame.quad = quad
        self.getPanel(0).populate()
        self.getPanel(1).populate()
    
class ComponentsInfoPanel(guibase.BasePanel):
    """Panel displays List of Components in Quad"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.quad = frame.quad
        numExtend = 1
        x = (self.frame.app.height - 768) / (30 * numExtend)
        cells = 11 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # component list
        self.lstItems = pyui.widgets.ListBox(self.onListSelected, None, 100, 100, 1)
        self.addChild(self.lstItems, (0, 0, 4, 6+x))
        self.btnRemove = pyui.widgets.Button('Remove Selected', self.onRemove)
        self.addChild(self.btnRemove, (0, 6+x, 4, 2))
        self.lblSP = pyui.widgets.Label(text='0 SP', type=1)
        self.addChild(self.lblSP, (0, 8+x, 4, 1))
        self.lblAP = pyui.widgets.Label(text='0 AP (energy)', type=1)
        self.addChild(self.lblAP, (0, 9+x, 4, 1))
        self.lblSlots = pyui.widgets.Label(text='0/0 components used', type=2)
        self.addChild(self.lblSlots, (0, 10+x, 4, 1))
        
        # pack widgets
        self.pack

    def onListSelected(self, item):
        """Enable Remove Button on List Selected"""
        if self.lstItems.getMultiSelectedItems() == []:
            self.btnRemove.disable()
        else:
            self.enableButtons(self.lstItems, [self.btnRemove])

    def onRemove(self, item):
        """Remove selected items"""
        list = self.lstItems.getMultiSelectedItems()
        # go through each component
        for item in list:
            myComponent = self.quad.components[item]
            if myComponent.weaponID == '':
                # this is not a weapon component remove it
                del self.quad.components[item]
                
        self.refreshPanel()

    def populate(self):
        """Populate panel with new data"""
        self.btnRemove.disable()
        self.quad = self.frame.quad
        # build components dict
        d = {}
        for componentID, myComponent in self.quad.components.iteritems():
            d[componentID] = self.frame.componentdata[myComponent.type].name
        # populate listbox
        self.populateListbox(self.lstItems, d)
        self.populateLabels()
        self.btnRemove.setText('Remove Components')
    
    def populateLabels(self):
        """Populate labels"""
        self.lblSP.setText('%d Shield Points' % self.quad.maxSP)
        self.lblAP.setText('%d Armor Points (%s)' % (self.quad.maxAP, self.quad.typeAP))
        try:
            self.lblSlots.setText('%d/%d components used' % (self.quad.currentComps, self.frame.shiphulldata[self.frame.mode.myShipDesign.shipHullID].componentNum))
        except:
            pass
    
    def refreshPanel(self):
        """Refresh the panel attributes"""
        self.quad.setMyStatus()
        self.frame.panel.populate(self.quad)
        self.frame.mode.updateDesign(1)
    
class WeaponsInfoPanel(ComponentsInfoPanel):
    """Panel displays List of Weapons in Quad"""

    def onRemove(self, item):
        """Remove selected items"""
        list = self.lstItems.getMultiSelectedItems()
        # go through each weapon
        for item in list:
            # remove weapon components first
            for componentID in self.quad.components.keys():
                myComponent = self.quad.components[componentID]
                if myComponent.weaponID == item:
                    del self.quad.components[myComponent.id]
            # then delete weapon
            del self.quad.weapons[item]
        
        self.refreshPanel()
                
    def populate(self):
        """Populate panel with new data"""
        self.btnRemove.disable()
        self.quad = self.frame.quad
        # build weapons dict
        d = {}
        for weaponID, myWeapon in self.quad.weapons.iteritems():
            d[weaponID] = '(%d)(%.2f)%s' % (myWeapon.facing, myWeapon.maxLock, self.frame.weapondata[myWeapon.type].name)
        # populate listbox
        self.populateListbox(self.lstItems, d)
        self.populateLabels()
        self.btnRemove.setText('Remove Weapons')
        
def main():
    """Run gui for testing"""
    import run
    import anwp.func.storedata
    width = 1024
    height = 768
    myGalaxy = anwp.func.storedata.loadFromFile('../../../Database/ANW1.anw')
    myShip = myGalaxy.ships['1']
    pyui.init(width, height, 'p3d', 0, 'Testing Quad Info Panel')
    app = run.TestApplication(width, height)
    i = 0
    top = 70
    width = (width/4)-20
    height = height/3
    dimensions = [(0, height, width, height), 
                  (width+10, top, width, height), 
                  (width*2+20, height, width, height), 
                  (width+10, top+height+150, width, height)]
    for position in ['aft', 'fore', 'port', 'star']:
        (x,y,w,h) = dimensions[i]
        myQuad = myShip.quads[position]
        frame = QuadInfoFrame(None, app, myQuad, x, y, w, h)
        app.addGui(frame)
        i += 1
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
