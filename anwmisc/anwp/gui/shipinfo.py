# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all Relevant Ship Information during a simulation
# ---------------------------------------------------------------------------
import string

import pyui
import guibase
import anwp.func.globals
import anwp.func.funcs

class ShipInfoFrame(guibase.BaseInfoFrame):
    """Displays Ship Information"""  
    def __init__(self, mode, app, ship, left=1):
        self.ship = ship
        title = ship.name
        guibase.BaseInfoFrame.__init__(self, mode, app, title, left)
        self.setPanel(TabbedInfoPanel(self))
        
    def signal(self, ship):
        """New subject calling frame"""
        self.ship = ship
        
        if self.currentID <> ship.gid:
            # different ship, populate panel
            self.currentID = ship.gid
            self.setPanel(TabbedInfoPanel(self))
            
        # populate panel
        self.panel.populate()

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the Ship"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.frame = frame
        self.addPanel('MAIN', ShipInfoPanel(frame))
        self.addPanel('FORE', QuadInfoPanel(frame, 'fore'))
        self.addPanel('STAR', QuadInfoPanel(frame, 'star'))
        self.addPanel('PORT', QuadInfoPanel(frame, 'port'))
        self.addPanel('AFT', QuadInfoPanel(frame, 'aft'))
        
    def populate(self):
        """When asked to populate the Panel will populate the active panel"""
        if self.frame.ship.name <> self.frame.title:
            self.frame.title = self.frame.ship.name
        self.activePanel.populate()
    
class ShipInfoPanel(guibase.BasePanel):
    """Panel displays main ship information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.ship = frame.ship
        numExtend = 1
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(6, cells))
        
        # ship id
        self.lblCaptain = pyui.widgets.Label(text='', type=1)
        self.addChild(self.lblCaptain, (0, 0, 6, 1))
        
        n = 2
        # general ship info
        self.lblISPA = pyui.widgets.Label(text='ISP:', type=1)
        self.addChild(self.lblISPA, (0, n, 2, 1))
        self.lblISPB = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblISPB, (2, n, 4, 1))
        self.lblPowerA = pyui.widgets.Label(text='POWER:', type=1)
        self.addChild(self.lblPowerA, (0, n+1, 2, 1))
        self.lblPowerB = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblPowerB, (2, n+1, 4, 1))
        self.lblBatteryA = pyui.widgets.Label(text='BATTERY:', type=1)
        self.addChild(self.lblBatteryA, (0, n+2, 2, 1))
        self.lblBatteryB = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblBatteryB, (2, n+2, 4, 1))
        self.lblAccelA = pyui.widgets.Label(text='ACCEL:', type=1)
        self.addChild(self.lblAccelA, (0, n+3, 2, 1))
        self.lblAccelB = pyui.widgets.Label(text='0 (MN)', type=2)
        self.addChild(self.lblAccelB, (2, n+3, 4, 1))
        self.lblRotationA = pyui.widgets.Label(text='ROTATION:', type=1)
        self.addChild(self.lblRotationA, (0, n+4, 2, 1))
        self.lblRotationB = pyui.widgets.Label(text='0', type=2)
        self.addChild(self.lblRotationB, (2, n+4, 4, 1))
        self.lblFacingA = pyui.widgets.Label(text='FACING:', type=1)
        self.addChild(self.lblFacingA, (0, n+5, 2, 1))
        self.lblFacingB = pyui.widgets.Label(text='0 deg', type=2)
        self.addChild(self.lblFacingB, (2, n+5, 4, 1))
        self.lblPositionA = pyui.widgets.Label(text='POSITION:', type=1)
        self.addChild(self.lblPositionA, (0, n+6, 2, 1))
        self.lblPositionB = pyui.widgets.Label(text='(0,0)', type=2)
        self.addChild(self.lblPositionB, (2, n+6, 4, 1))
        
        # port
        n = 10
        self.lblTitle2 = pyui.widgets.Label(text='QUADRANT INFORMATION:', type=1)
        self.addChild(self.lblTitle2, (0, n-1, 4, 1))
        if self.frame.mode <> None:
            if self.frame.mode.__module__ == 'anwp.modes.modebattle':
                if self.frame.mode.game.myEmpire['designsLeft'] > 0:
                    self.btnCopyDesign = pyui.widgets.Button('Copy Design', self.onCopyDesign)
                    self.addChild(self.btnCopyDesign, (4, n-1, 2, 1))
        self.lblTitle2.setColor(anwp.func.globals.colors['black'])
        self.lblPort = pyui.widgets.Label(text='PORT', type=1)
        self.addChild(self.lblPort, (2, n, 2, 1))
        self.lblportSP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblportSP, (2, n+1, 2, 1))
        self.lblportAP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblportAP, (2, n+2, 2, 1))
        self.lblportComps = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblportComps, (2, n+3, 2, 1))

        # aft
        self.lblAft = pyui.widgets.Label(text='AFT', type=1)
        self.addChild(self.lblAft, (0, n+4, 2, 1))
        self.lblaftSP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblaftSP, (0, n+5, 2, 1))
        self.lblaftAP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblaftAP, (0, n+6, 2, 1))
        self.lblaftComps = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblaftComps, (0, n+7, 2, 1))
        
        # picture
        self.pctShip = pyui.widgets.Picture('')
        self.addChild(self.pctShip, (2, n+4, 2, 4))
        
        # fore
        self.lblFore = pyui.widgets.Label(text='FORE', type=1)
        self.addChild(self.lblFore, (4, n+4, 2, 1))
        self.lblforeSP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblforeSP, (4, n+5, 2, 1))
        self.lblforeAP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblforeAP, (4, n+6, 2, 1))
        self.lblforeComps = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblforeComps, (4, n+7, 2, 1))
        
        # star
        self.lblStar = pyui.widgets.Label(text='STAR', type=1)
        self.addChild(self.lblStar, (2, n+8, 2, 1))
        self.lblstarSP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblstarSP, (2, n+9, 2, 1))
        self.lblstarAP = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblstarAP, (2, n+10, 2, 1))
        self.lblstarComps = pyui.widgets.Label(text='0/0', type=2)
        self.addChild(self.lblstarComps, (2, n+11, 2, 1))
        
        # weapons
        n = n + 12
        self.lblTitle3 = pyui.widgets.Label(text='WEAPON INFORMATION:', type=1)
        self.addChild(self.lblTitle3, (0, n, 6, 1))
        self.lblTitle3.setColor(anwp.func.globals.colors['black'])
        self.shtWeapons = pyui.sheet.Sheet()
        self.shtWeapons.setColumnTitle(1, 'weap')
        self.shtWeapons.setColumnWidth(1,55)
        self.shtWeapons.setColumnTitle(2, 'curLock')
        self.shtWeapons.setColumnWidth(2,80)
        self.shtWeapons.setColumnTitle(3, 'maxLock')
        self.shtWeapons.setColumnWidth(3,80)
        self.shtWeapons.setColumnTitle(4, 'power')
        self.shtWeapons.setColumnWidth(4,60)
        self.shtWeapons.setColumnTitle(5, 'ammo')
        self.shtWeapons.setColumnWidth(5,55)
        
        self.addChild(self.shtWeapons, (0, n+1, 6, 5+x))
        
        i = 1
        for position in ['fore', 'star', 'port', 'aft']:
            myQuad = self.ship.quads[position]
            for weaponID in anwp.func.funcs.sortStringList(myQuad.weapons.keys()):
                myWeapon = myQuad.weapons[weaponID]
                self.shtWeapons.setCellValue(1, i, myWeapon.myWeaponData.abr)
                self.shtWeapons.setCellValue(2, i, '0')
                self.shtWeapons.setCellValue(3, i, '0')
                self.shtWeapons.setCellValue(4, i, '0')
                i += 1

        # pack widgets
        self.pack
        self.populate()

    def onCopyDesign(self, item):
        """Copy Ship Design"""
        self.frame.mode.modeYesNoBox('Do you wish to use up a Design to copy This Design?', 'copyDesignYes', 'copyDesignNo')

    def populate(self):
        """Populate frame with new data"""
        try:
            shipImageName = '%s.png' % self.ship.myDesign.getImageFileName()
            if shipImageName not in self.frame.mode.game.imageFileList:
                myShipPict = '%squestion.png' % (self.frame.app.genImagePath, shipImageName)
            else:
                myShipPict = '%s%s' % (self.frame.app.simImagePath, shipImageName)
        except:
            myShipPict = '%squestion.png' % (self.frame.app.genImagePath)
        
        self.pctShip.setFilename(myShipPict)
        
        # ship info
        self.lblCaptain.setText('%s - (%.2f)' % (self.ship.myCaptain.fullName, self.ship.myCaptain.experience))
        self.lblISPB.setText('%.2f/%.2f' % (self.ship.currentISP, self.ship.myShipHull.maxISP))
        self.lblISPB.setColor(anwp.func.funcs.getDamageColor(self.ship.currentISP, self.ship.myShipHull.maxISP))
        self.lblPowerB.setText('%.2f/%.2f' % (self.ship.currentPower, self.ship.myDesign.maxPower))
        self.lblPowerB.setColor(anwp.func.funcs.getDamageColor(self.ship.currentPower, self.ship.myDesign.maxPower))
        self.lblBatteryB.setText('%d/%d' % (self.ship.currentBattery, self.ship.myDesign.maxBattery))
        self.lblBatteryB.setColor(anwp.func.funcs.getDamageColor(self.ship.currentBattery, self.ship.myDesign.maxBattery))
        self.lblAccelB.setText('%.2f' % (self.ship.accel))
        self.lblRotationB.setText('%.2f' % (self.ship.rotation))
        self.lblFacingB.setText('%d (deg)' % (self.ship.facing))
        self.lblPositionB.setText('(%d,%d)' % (self.ship.posX, self.ship.posY))
        
        # quadrant info
        for position, myQuad in self.ship.quads.iteritems():
            spLabel = getattr(self, 'lbl%sSP' % position)
            spLabel.setText('%d/%d' % (myQuad.currentSP, myQuad.maxSP))
            spLabel.setColor(anwp.func.globals.colors['green'])
            apLabel = getattr(self, 'lbl%sAP' % position)
            apLabel.setText('%d/%d' % (myQuad.currentAP, myQuad.maxAP))
            apLabel.setColor(anwp.func.globals.colors['blue'])
            compsLabel = getattr(self, 'lbl%sComps' % position)
            current = myQuad.currentComps
            max = self.ship.myDesign.myShipHull.componentNum
            compsLabel.setText('%d/%d' % (current, max))
            compsLabel.setColor(anwp.func.funcs.getDamageColor(current, max))
        
        # weapons
        i = 1
        for position in ['fore', 'star', 'port', 'aft']:
            myQuad = self.ship.quads[position]
            for weaponID in anwp.func.funcs.sortStringList(myQuad.weapons.keys()):
                myWeapon = myQuad.weapons[weaponID]
                if myWeapon.operational == 1:
                    self.shtWeapons.setCellValue(2, i, '%.2f' % (myWeapon.currentLock))
                    self.shtWeapons.setCellValue(3, i, '%.2f' % (myWeapon.maxLock))
                    self.shtWeapons.setCellValue(4, i, '%d' % (myWeapon.currentPower))
                    self.shtWeapons.setCellValue(5, i, '%d' % (myWeapon.availAmmo))
                else:
                    self.shtWeapons.setCellValue(2, i, 'Disable')
                    self.shtWeapons.setCellValue(3, i, '-------')
                    self.shtWeapons.setCellValue(4, i, '-------')
                    self.shtWeapons.setCellValue(5, i, str(myWeapon.availAmmo))
                i += 1
    
class QuadInfoPanel(guibase.BasePanel):
    """Panel displays main ship quad information"""
    def __init__(self, frame, position):
        guibase.BasePanel.__init__(self, frame)
        self.myQuad = frame.ship.quads[position]
        self.designQuad = frame.ship.myDesign.quads[position]
        numExtend = 1
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(6, cells))
        
        # components
        self.lbl = pyui.widgets.Label(text='%s QUADRANT COMPONENTS:' % string.upper(self.myQuad.position), type=1)
        self.addChild(self.lbl, (0, 1, 2, 1))
        
        n = 2
        self.shtComponents = pyui.sheet.Sheet()
        self.shtComponents.setColumnTitle(1, 'component')
        self.shtComponents.setColumnWidth(1, 260)
        self.shtComponents.setColumnTitle(2, 'status')
        self.shtComponents.setColumnWidth(2, 40)
        self.addChild(self.shtComponents, (0, n, 6, 26+x))
        
        i = 1
        for componentID in anwp.func.funcs.sortStringList(self.designQuad.components.keys()):
            designComponent = self.designQuad.components[componentID]
            self.shtComponents.setCellValue(1, i, designComponent.myComponentData.name)
            self.shtComponents.setCellValue(2, i, 'active')
            i += 1
        
        # pack widgets
        self.pack
        self.populate()

    def populate(self):
        """Populate frame with new data"""
        # components
        i = 1
        for componentID in anwp.func.funcs.sortStringList(self.designQuad.components.keys()):
            designComponent = self.designQuad.components[componentID]
            if componentID not in self.myQuad.components:
                self.shtComponents.setCellValue(2, i, 'Gone')
            elif designComponent.currentHP < designComponent.myComponentData.maxHP:
                self.shtComponents.setCellValue(2, i, 'Damaged')
            else:
                self.shtComponents.setCellValue(2, i, 'Active')
            i += 1

def main():
    """Run gui for testing"""
    import run
    import anwp.func.storedata
    width = 1024
    height = 768
    myGalaxy = anwp.func.storedata.loadFromFile('../../../Database/ANW.anw')
    myShip = myGalaxy.ships['1']
    pyui.init(width, height, 'p3d', 0, 'Testing Ship Info Panel')
    app = run.TestApplication(width, height)
    frame = ShipInfoFrame(None, app, myShip)
    frame.panel.populate()
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
