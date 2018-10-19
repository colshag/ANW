# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipdesignvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to 
# Add/Remove Weapons and Components for a selected Ship Design
# ---------------------------------------------------------------------------
import string

from anw.func import globals, funcs
from anw.gui import textonscreen, scrollvalue, weapondirection

class ShipDesignValue(scrollvalue.ScrollValue):
    """Add or remove ship design weapons and components"""
    def __init__(self, path, id, myParent):
        self.weapondirection = None
        self.isWeapon = 0
        self.isDrone = 0
        self.myDroneDesign = None
        self.myParent = myParent
        self.mode = myParent.mode
        self.game = myParent.game
        self.id = self.getID(id)
        self.myShipDesign = myParent.myShipDesign
        self.myData = self.getMyData()
        self.sim = None
        self.textName = None
        self.textDescription = None
        self.textCR = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        scrollvalue.ScrollValue.__init__(self, path, x=0.42, y=-0.72, name='design')
        self.allKeys = ['A','S','D','Z','X','C','V']
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C', 'V']
        self.scrollFactor = 1
        self.selectedQuad = ''
        self.myTitle.setText('Add or Remove Selected item from Quadrant:')
        self.createMyInfo()
        if self.isWeapon == 1:
            self.createWeaponDirection()
    
    def setMyDroneDesign(self, droneID):
        """Set the DroneDesign"""
        self.myDroneDesign = self.mode.game.droneDesignObjects[droneID]
    
    def getID(self, id):
        """id will be prefixed with a W to denote a weapon, D for a drone, instead of ship component"""
        if id[0] == 'W':
            self.isWeapon = 1
            return id[1:]
        elif id[0] == 'D':
            self.isWeapon = 1
            self.isDrone = 1
            self.setMyDroneDesign(id[1:])
            self.myParent.createDroneInfo(self.myDroneDesign)
            return self.myDroneDesign.getMyLauncherID()
        else:
            self.isWeapon = 0
            return id
    
    def createWeaponDirection(self):
        """Display Weapon Direction Buttons"""
        if self.weapondirection == None:
            self.weapondirection = weapondirection.WeaponDirection(self.path, x=0.42, y=-0.9)
            self.myWidgets.append(self.weapondirection)
    
    def getMyData(self):
        """MyData is either a componentData object or weaponData object"""
        if self.isWeapon == 1:
            return self.myParent.mode.game.weapondata[self.id]
        else:
            return self.myParent.mode.game.componentdata[self.id]
    
    def createButtons(self):
        """Create all Buttons"""
        for key in ['Z','X','C','V']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
        self.x = 0
        self.y = 1
        for key in ['A','S','D']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
    
    def pressZ(self):
        """Press Fore Quad"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.selectedQuad = 'fore'
        self.setMin()
        self.setMax()
    
    def pressX(self):
        """Press Aft Quad"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.selectedQuad = 'aft'
        self.setMin()
        self.setMax()
    
    def pressC(self):
        """Press Port Quad"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.selectedQuad = 'port'
        self.setMin()
        self.setMax()
    
    def pressV(self):
        """Press Star Quad"""
        self.enableLastButton('V')
        self.disableButton('V')
        self.selectedQuad = 'star'
        self.setMin()
        self.setMax()

    def createMyInfo(self):
        """Create Info based on id given"""
        self.setCurrentValue(0)
        self.writeName()
        self.createSim()
        self.writeDescription()
        self.writeCost()
    
    def setMin(self):
        """Min is based on number of that component or weapon type in quad"""
        try:
            myQuad = self.myShipDesign.quads[self.selectedQuad]
            count = 0
            if self.isWeapon == 1:
                for weaponID, myWeapon in myQuad.weapons.iteritems():
                    if myWeapon.type == self.myData.id:
                        count += 1
            else:
                for componentID, myComponent in myQuad.components.iteritems():
                    if myComponent.type == self.myData.id:
                        count += 1
            self.setMinValue(-count)
        except:
            self.setMinValue(0)
    
    def setMax(self):
        """Max is based on remaining component slots and weapon size in comps"""
        try:
            num = self.myShipDesign.myShipHull.componentNum
            num = num-self.myShipDesign.quads[self.selectedQuad].currentComps
            if self.isWeapon == 1:
                num = num/self.myData.numComps
            self.setMaxValue(num)
        except:
            self.setMaxValue(0)
    
    def writeName(self):
        """Create Name"""
        if self.textName == None:
            self.textName = textonscreen.TextOnScreen(self.path, self.myData.name,
                                                          scale=0.04, font=5, parent=aspect2d)
            self.textName.writeTextToScreen(self.posInitX+0.36, 0, self.posInitY+0.31, 12)
            self.textName.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 7, 0.2)
            self.myWidgets.append(self.textName)
        else:
            self.textName.myText.setText(self.myData.name)
    
    def createSim(self):
        """Create myData Sim Picture"""
        if len(self.myData.abr) == 4:
            name = 'ammo'
        else:
            name = string.lower(self.myData.abr[1:])
        if self.sim == None:
            self.sim = loader.loadModelCopy('%s/plane' % self.path)
            self.sim.setScale(0.08)
            self.sim.reparentTo(aspect2d)
            self.sim.setTransparency(1)
            tex = loader.loadTexture('%s/%s.png' % (self.path, name))
            self.sim.setTexture(tex, 0)
            self.sim.setPos(self.posInitX+0.41, 0, self.posInitY+0.17)
            self.myWidgets.append(self.sim)
        else:
            tex = loader.loadTexture('%s/%s.png' % (self.path, name))
            self.sim.setTexture(tex, 0)
    
    def writeDescription(self):
        """Create Description"""
        if self.textDescription == None:
            self.textDescription = textonscreen.TextOnScreen(self.path, self.myData.description,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textDescription.writeTextToScreen(self.posInitX+0.36, 0, self.posInitY+0.09, 20)
            self.textDescription.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.myWidgets.append(self.textDescription)
        else:
            self.textDescription.myText.setText(self.myData.description)
    
    def writeCost(self):
        """Create Cost"""
        self.writeCRCost()
        self.writeALCost()
        self.writeECCost()
        self.writeIACost()
    
    def writeCRCost(self):
        value = '%d' % (self.myData.costCR)
        if self.textCR == None:
            self.textCR = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textCR.writeTextToScreen(self.posInitX+0.47, 0, self.posInitY+0.2, 10)
            self.textCR.setColor(globals.colors['guigreen'])
            self.myWidgets.append(self.textCR)
        else:
            self.textCR.myText.setText(value)
    
    def writeALCost(self):
        value = '%d' % (self.myData.costAL)
        if self.textAL == None:
            self.textAL = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textAL.writeTextToScreen(self.posInitX+0.47, 0, self.posInitY+0.2-0.02, 10)
            self.textAL.setColor(globals.colors['guiblue1'])
            self.myWidgets.append(self.textAL)
        else:
            self.textAL.myText.setText(value)
    
    def writeECCost(self):
        value = '%d' % (self.myData.costEC)
        if self.textEC == None:
            self.textEC = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textEC.writeTextToScreen(self.posInitX+0.47, 0, self.posInitY+0.2-0.04, 10)
            self.textEC.setColor(globals.colors['guiyellow'])
            self.myWidgets.append(self.textEC)
        else:
            self.textEC.myText.setText(value)
    
    def writeIACost(self):
        value = '%d' % (self.myData.costIA)
        if self.textIA == None:
            self.textIA = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textIA.writeTextToScreen(self.posInitX+0.47, 0, self.posInitY+0.2-0.06, 10)
            self.textIA.setColor(globals.colors['guired'])
            self.myWidgets.append(self.textIA)
        else:
            self.textIA.myText.setText(value)
    
    def pressS(self):
        """Submit value"""
        myQuad = self.myShipDesign.quads[self.selectedQuad]
        if self.myDroneDesign == None:
            droneID = ''
        else:
            droneID = self.myDroneDesign.id
        if self.isWeapon == 1:
            if self.currentValue < 0:
                self.myParent.removeWeapons(myQuad, self.myData.id, -self.currentValue)
            else:
                self.myParent.addWeapons(myQuad, self.myData.id, self.currentValue, self.weapondirection.direction, droneID)
        else:
            if self.currentValue < 0:
                self.myParent.removeComponents(myQuad, self.myData.id, -self.currentValue)
            else:
                self.myParent.addComponents(myQuad, self.myData.id, self.currentValue)
        self.disableButton('S')
    
    def ignoreShortcuts(self):
        """Ignore all keyboard shortcuts created"""
        self.ignoreAll()
        if self.weapondirection != None:
            self.weapondirection.ignoreShortcuts()
    
    def setShortcuts(self):
        """Set all keyboard shortcuts"""
        for key in self.allKeys:
            self.setAcceptOnButton(key)
        if self.weapondirection != None:
            self.weapondirection.setShortcuts()