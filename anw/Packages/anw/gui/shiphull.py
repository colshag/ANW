# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shiphull.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The system represents one Ship Hull object in design mode
# ---------------------------------------------------------------------------
import string
import direct.directbase.DirectStart
from anw.gui import textonscreen, rootsim, buttonlist, textentry
from anw.gui import shipdesignvalue, valuebar, designinfo, designsubmit, designchoosebv
from anw.func import globals, funcs
        
class ShipHull(rootsim.RootSim):
    """A Ship Hull Gui for selecting Ship Hull in Design Mode
    Ship Design displayed via Ship Hull"""
    def __init__(self, path, mode, empireID, myShipHull, x, z):
        self.enableMouseCamControl = 0
        self.myShipHull = myShipHull
        self.id = self.myShipHull.id
        self.empireID = empireID
        self.color1 = globals.empires[int(self.empireID)]['color1']
        self.color2 = globals.empires[int(self.empireID)]['color2']
        myTexture = '%sb_%s' % (string.lower(myShipHull.abr), self.empireID)
        rootsim.RootSim.__init__(self, path, myTexture, 'plane', transparent=1, scale=0.5)
        self.resourceSize = 0.1
        self.mode = mode
        self.myShipDesign = None
        self.textName = None
        self.textCR = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        self.aftQuadInfo = None
        self.portQuadInfo = None
        self.foreQuadInfo = None
        self.starQuadInfo = None
        self.componentdata = None
        self.weapondata = None
        self.shipdesignvalue = None
        self.componentlist = None
        self.weaponlist = None
        self.designCost = None
        self.designInfo = None
        self.droneInfo = None
        self.allDesignsList = None
        self.designNameEntry = None
        self.designSubmit = None
        self.myBV = 0.0
        self.otherBV = 0.0
        self.chooseBV = None
        self.x = x
        self.y = 20
        self.z = z
        self.ageColor = ['guigreen','guiyellow','orange']
        self.createMySim()
    
    def setupShipDesign(self, compDict, weapDict, name):
        """Setup the Ship design based on compDict and weapDict"""
        self.clearMyText()
        self.componentdata = self.mode.game.componentdata
        self.weapondata = self.mode.game.weapondata
        self.myShipDesign = self.mode.game.getShipDesign('1', self.id, compDict, weapDict, name)
        self.mode.designName = self.getShipDesignName()
        self.createQuads()
        self.createWeaponList()
        self.createComponentList()
        self.createDesignInfo()
        self.createDesignNameEntry()
        self.createDesignSubmit()
    
    def createDesignSubmit(self):
        self.designSubmit = designsubmit.DesignSubmit(self.path, self.mode, self.myShipDesign, x=0.75, z=-0.3)
        self.myWidgets.append(self.designSubmit)
    
    def createDesignNameEntry(self):
        self.designNameEntry = textentry.TextEntry(self.path, self.mode, command='onDesignNameEntered',
                                                   initialText=self.mode.designName,
                                                   title='Enter Ship Design Below:', lines=1, width=18, 
                                                   x=0.7, z=0.07, font=5, titleWidth=20, textDelta=0.075)
        self.myWidgets.append(self.designNameEntry)
    
    def getShipDesignName(self):
        """Ships come with a ABR-name, remove the ABR-"""
        name = self.myShipDesign.name
        if '-' in name[:6]:
            for char in name:
                if char != '-':
                    name = name[1:]
                else:
                    return name[1:]
        return name
    
    def clearSimulateDesign(self):
        """Clear any gui associated with simulating design"""
        self.removeWidget(self.allDesignsList)
        self.removeWidget(self.chooseBV)
        self.myBV = 0.0
        self.otherBV = 0.0
    
    def createChooseBV(self, otherDesignID):
        """Create the Choose BattleValue (BV) gui for simulate against design"""
        self.clearSimulateDesign()
        self.chooseBV = designchoosebv.DesignChooseBV(self.path, otherDesignID)
        self.chooseBV.setMyMode(self.mode)
        self.myWidgets.append(self.chooseBV)
        
    def createDesignInfo(self):
        """Display Design Info"""
        self.removeDesignInfo()
        self.designInfo = designinfo.DesignInfo(self.path, self.empireID,
                                                self.myShipDesign, 0.5, 0.79)
        self.designInfo.setMyMode(self.mode)
        self.designInfo.writeAttributes()
        self.myWidgets.append(self.designInfo)

    def removeDesignInfo(self):
        if self.designInfo != None:
            self.removeWidget(self.designInfo)
        
    def createDroneInfo(self, droneDesign):
        """Display Drone Design Info for a Drone being selected as a weapon"""
        self.removeDroneInfo()
        self.droneInfo = designinfo.DesignInfo(self.path, self.empireID,
                                                droneDesign, -1.12, 0.18)
        self.droneInfo.setMyMode(self.mode)
        self.droneInfo.writeAttributes()
        self.myWidgets.append(self.droneInfo)
    
    def removeDroneInfo(self):
        if self.droneInfo != None:
            self.removeWidget(self.droneInfo)
    
    def updateDesignInfo(self):
        """Update the Info for Design"""
        self.myShipDesign.setMyStatus()
        self.removeDroneInfo()
        self.removeWidget(self.designInfo)
        self.createDesignInfo()
    
    def removeShipDesign(self):
        """Remove all indicators of ship design zoom"""
        if self.aftQuadInfo != None:
            self.aftQuadInfo.destroy()
        if self.foreQuadInfo != None:
            self.foreQuadInfo.destroy()
        if self.portQuadInfo != None:
            self.portQuadInfo.destroy()
        if self.starQuadInfo != None:
            self.starQuadInfo.destroy()
        self.removeWidget(self.shipdesignvalue)
        self.removeWidget(self.weaponlist)
        self.removeWidget(self.componentlist)
        self.removeWidget(self.designInfo)
        self.removeWidget(self.droneInfo)
        self.removeWidget(self.designNameEntry)
        self.removeWidget(self.designSubmit)
        self.clearSimulateDesign()
        self.mode.designName = ''
        
    def createQuads(self):
        """Create the 4 Quadrant lists displaying design component info"""
        for (quad, (x,z)) in {'fore':(0.03,0.5),'aft':(0.03,-0.7),'port':(-0.32,-0.1),'star':(0.38,-0.1)}.iteritems():
            text = self.getTextFromQuad(quad)
            setattr(self, '%sQuadInfo' % quad, buttonlist.ButtonList(self.path, text, width=0.6, height=0.50))
            myQuad = getattr(self, '%sQuadInfo' % quad)
            myQuad.setMyPosition(x,z)
            myQuad.setMyMode(self)
            myQuad.setOnClickMethod('%sQuadClicked' % quad)
            self.myWidgets.append(myQuad)
            self.populateQuadInfo(quad)
    
    def createAllDesignsList(self):
        """List other ship designs"""
        self.removeWidget(self.shipdesignvalue)
        text = 'Choose a Ship Design to Test Against:'
        self.allDesignsList = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.allDesignsList.setMyPosition(0.8,-0.65)
        self.allDesignsList.setMyMode(self)
        self.allDesignsList.setOnClickMethod('allDesignsListClicked')
        self.myWidgets.append(self.allDesignsList)
        self.populateAllDesignsList()
    
    def populateAllDesignsList(self):
        """Add All Designs to the List"""
        for shipDesignID in funcs.sortStringList(self.game.shipDesigns.keys()):
            myShipDesign = self.game.shipDesignObjects[shipDesignID]
            if self.mode.allTech == 1 or myShipDesign.hasAllTech == 1:
                self.allDesignsList.myScrolledList.addItem(text=myShipDesign.name, extraArgs=shipDesignID)
    
    def allDesignsListClicked(self, otherDesignID, index, button):
        """Design selected to test against"""
        self.createChooseBV(otherDesignID)        
    
    def simulateMyDesign(self, otherDesignID):
        """Simulate against Chosen Design"""
        myShipDesign = self.designSubmit.myDesign
        myShipDesign.name = self.mode.designName
        otherShipDesign = self.game.shipDesignObjects[otherDesignID]
        self.mode.setEmpireValues({'simulationsLeft':self.game.myEmpire['simulationsLeft']-1})
        multiSimDict = {1:{myShipDesign:self.myBV},
                        2:{otherShipDesign:self.otherBV}
                        }
        self.game.currentDesign = myShipDesign
        self.mode.resetMode()
        self.game.createShipSimulation(multiSimDict)
        
    def createWeaponList(self):
        """List all Weapons that can be added to design"""
        text = 'Choose a Weapon Type:'
        self.weaponlist = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.weaponlist.setMyPosition(-0.8,0.5)
        self.weaponlist.setMyMode(self)
        self.weaponlist.setOnClickMethod('componentListClicked')
        self.myWidgets.append(self.weaponlist)
        self.populateWeaponList()
    
    def populateWeaponList(self):
        """Add Weapons to List based on alltech or mytech"""
        myWeaponList = funcs.sortStringList(self.weapondata.keys())
        myAges = self.getDataIntoTechAges(myWeaponList, self.weapondata)
        count = 0
        for AgeList in myAges:
            for myWeaponData in AgeList:
                if self.mode.allTech == 1 or self.mode.game.myTech[myWeaponData.techReq].complete == 1:
                    if (myWeaponData.abr not in globals.weaponLimitations[self.myShipHull.function] and
                        myWeaponData.abr[2:] != 'L'):
                        self.weaponlist.myScrolledList.addItem(text=myWeaponData.name,
                                                               extraArgs='W' + myWeaponData.id, 
                                                               textColorName=self.ageColor[count])
            count += 1
        self.populateDronesToList()
    
    def getDataIntoTechAges(self, myList, dataType):
        myAges = [[],[],[]]
        for id in myList:
            myData = dataType[id]
            if int(myData.techReq) < 100:
                myAges[2].append(myData)
            elif int(myData.techReq) < 200:
                myAges[1].append(myData)
            else:
                myAges[0].append(myData)
        return myAges
        
    def populateDronesToList(self):
        """Carriers or Platforms can add drones as weapons"""
        if self.myShipHull.function in ('carrier', 'platform'):
            for droneDesignID in funcs.sortStringList(self.mode.game.droneDesigns.keys()):
                myDroneDesign = self.mode.game.droneDesignObjects[droneDesignID]
                if self.mode.allTech == 1 or myDroneDesign.hasAllTech == 1:
                    self.weaponlist.myScrolledList.addItem(text=myDroneDesign.name, extraArgs='D' + droneDesignID)
        

    def createComponentList(self):
        """List all Components that can be added to design"""
        text = 'Choose a Component Type:'
        self.componentlist = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.componentlist.setMyPosition(-0.8,-0.65)
        self.componentlist.setMyMode(self)
        self.componentlist.setOnClickMethod('componentListClicked')
        self.myWidgets.append(self.componentlist)
        self.populateComponentList()
    
    def populateComponentList(self):
        """Add Components based on alltech or mytech"""
        myComponentList = funcs.sortStringList(self.componentdata.keys())
        myAges = self.getDataIntoTechAges(myComponentList, self.componentdata)
        count = 0
        for AgeList in myAges:
            for myComponentData in AgeList:
                if myComponentData.name != 'Weapon Component':
                    if self.mode.allTech == 1 or self.mode.game.myTech[myComponentData.techReq].complete == 1:
                        if (myComponentData.abr not in globals.componentLimitations[self.myShipHull.function] and
                            myComponentData.abr not in ['CSE','CRT']):
                            self.componentlist.myScrolledList.addItem(text=myComponentData.name,
                                                                      extraArgs='%s' % myComponentData.id, 
                                                                      textColorName=self.ageColor[count])
                        elif (myComponentData.abr not in globals.componentLimitations[self.myShipHull.function] and
                              self.id in ['8','9','10','11','12'] ):
                            self.componentlist.myScrolledList.addItem(text=myComponentData.name,
                                                                  extraArgs='%s' % myComponentData.id, 
                                                                  textColorName=self.ageColor[count])
            count += 1
    
    def getTextFromQuad(self, quad):
        """Return detailed info of Quadrant in text form"""
        myQuad = self.myShipDesign.quads[quad]
        text = '%s: %d SH : %d AR : (%d/%d)' % (string.upper(quad),
                                                myQuad.maxSP,myQuad.maxAP,
                                                myQuad.currentComps,
                                                self.myShipHull.componentNum)
        return text
    
    def foreQuadClicked(self, id, index, button):
        self.clearOtherQuads('fore')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressZ()
    
    def aftQuadClicked(self, id, index, button):
        self.clearOtherQuads('aft')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressX()

    def portQuadClicked(self, id, index, button):
        self.clearOtherQuads('port')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressC()
    
    def starQuadClicked(self, id, index, button):
        self.clearOtherQuads('star')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressV()
        
    def componentListClicked(self, id, index, button):
        self.clearOtherQuads('')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressZ()

    def clearOtherQuads(self, quad):
        for name in ['fore','aft','port','star']:
            if name != quad:
                myQuadList = getattr(self, '%sQuadInfo' % name)
                myQuadList.myScrolledList.restoreNodeButton2Normal()
        self.componentlist.myScrolledList.restoreNodeButton2Normal()
        self.weaponlist.myScrolledList.restoreNodeButton2Normal()
        self.clearSimulateDesign()

    def createShipDesignValue(self, id):
        self.mode.playSound('beep01')
        self.removeWidget(self.shipdesignvalue)
        self.removeDroneInfo()
        self.shipdesignvalue = shipdesignvalue.ShipDesignValue(self.path, id, self)
        self.myWidgets.append(self.shipdesignvalue)

    def populateQuadInfo(self, quad):
        """Fill the appropriate QuadInfo Listbox with component info"""
        myQuad = getattr(self, '%sQuadInfo' % quad)
        for weaponID, myWeapon in self.myShipDesign.quads[quad].weapons.iteritems():
            if myWeapon.myWeaponData.abr[2:]  == 'L':
                myDroneDesign = self.mode.game.droneDesignObjects[myWeapon.droneID]
                myQuad.myScrolledList.addItem(text='%s(%.2f)%s' % (self.getWeaponFacing(myWeapon.facing), myWeapon.maxLock, myDroneDesign.name),
                                              extraArgs='D' + myDroneDesign.id)
            else:
                myQuad.myScrolledList.addItem(text='%s(%.2f)%s' % (self.getWeaponFacing(myWeapon.facing), myWeapon.maxLock, self.weapondata[myWeapon.type].name),
                                              extraArgs='W' + myWeapon.type,
                                              textColorName=self.getAgeColor(myWeapon.myWeaponData.techReq))
        for myComponent in funcs.sortDictByChildObjValue(self.myShipDesign.quads[quad].components, 'type'):
            if myComponent.weaponID == '':
                myQuad.myScrolledList.addItem(text=self.componentdata[myComponent.type].name,
                                              extraArgs=myComponent.type, 
                                              textColorName=self.getAgeColor(myComponent.myComponentData.techReq))

    def getWeaponFacing(self, facing):
        if facing in globals.angleQuads:
            return globals.angleQuads[facing]
        else:
            return '%d' % facing

    def getAgeColor(self, techReq):
        try:
            if int(techReq) < 100:
                return self.ageColor[2]
            elif int(techReq) < 200:
                return self.ageColor[1]
            else:
                return self.ageColor[0]
        except:
            return 'guiwhite'
        
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.setColor()
        self.setPos()
        self.displayMyText()
    
    def destroy(self):
        """Remove from game"""
        self.removeMyWidgets()
        self.sim.removeNode()
        self.clearText(self.textName)
        self.clearText(self.textCR)
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
    
    def writeName(self):
        """Write the name"""
        self.textName = textonscreen.TextOnScreen(self.path, self.myShipHull.name, 0.15, font=3)
        self.textName.writeTextToScreen(self.x-0.27, self.y, self.z+0.5, wordwrap=7)
        self.textName.setColor(globals.colors[self.color1])
    
    def writeResources(self):
        """Display any available resources"""
        self.resourceCount = 0
        for resource in ['CR','AL','EC','IA']:
            value = getattr(self.myShipHull, 'cost%s' % resource)
            if value > 0:
                myMethod = getattr(self, 'write%s' % resource)
                myMethod(self.x-0.27, self.y, self.z-0.3-(0.12*self.resourceCount), value)
                self.resourceCount += 1
    
    def clearMyText(self):
        """clear Text around ship"""
        self.clearText(self.textName)
        self.clearText(self.textCR)
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
    
    def displayMyText(self):
        """Show text around ship"""
        self.writeName()
        self.writeResources()
    
    def addWeapons(self, myQuad, id, amount, weaponPosition, droneID):
        """Add weapons to Quad"""
        while amount > 0:
            self.myShipDesign.addWeapon(id, myQuad.position, weaponPosition, droneID)
            amount -= 1
        self.resetShipDesignInfo(myQuad.position)    
    
    def removeComponents(self, myQuad, id, amount):
        """Remove Components from Quad"""
        for componentID in myQuad.components.keys():
            myComponent = myQuad.components[componentID]
            if myComponent.type == id and amount > 0:
                del myQuad.components[componentID]
                amount -= 1
        self.resetShipDesignInfo(myQuad.position)
    
    def removeWeapons(self, myQuad, id, amount):
        """Remove weapons on Quad"""
        for weaponID in myQuad.weapons.keys():
            myWeapon = myQuad.weapons[weaponID]
            if myWeapon.type == id and amount > 0:
                del myQuad.weapons[weaponID]
                for componentID in myQuad.components.keys():
                    myComponent = myQuad.components[componentID]
                    if myComponent.weaponID == weaponID:
                        del myQuad.components[componentID]
                amount -= 1
        self.resetShipDesignInfo(myQuad.position)
        
    def addComponents(self, myQuad, id, amount):
        """Add Components to Quad"""
        while amount > 0:
            self.myShipDesign.addComponent(id, myQuad.position)
            amount -= 1
        self.resetShipDesignInfo(myQuad.position)
    
    def resetShipDesignInfo(self, quad):
        """Reset the info now that design has been modified"""
        self.removeWidget(self.shipdesignvalue)
        self.myShipDesign.setMyStatus()
        myQuadList = getattr(self, '%sQuadInfo' % quad)
        myQuadList.myTitle.myText.setText(self.getTextFromQuad(quad))
        myQuadList.myScrolledList.clear()
        self.populateQuadInfo(quad)
        self.updateDesignInfo()
    
    def ignoreShortcuts(self):
        if self.shipdesignvalue != None:
            self.shipdesignvalue.ignoreShortcuts()
    
    def setShortcuts(self):
        if self.shipdesignvalue != None:
            self.shipdesignvalue.setShortcuts()
    
class DroneHull(ShipHull):
    """A Drone Hull is like a Ship Hull, but only one quadrant available for design"""
    
    def setupShipDesign(self, compDict, weapDict, name):
        """Setup the Ship design based on compDict and weapDict"""
        self.clearMyText()
        self.componentdata = self.mode.game.componentdata
        self.weapondata = self.mode.game.weapondata
        self.myShipDesign = self.mode.game.getDroneDesign('1', self.id, compDict, weapDict, name)
        self.mode.designName = self.getShipDesignName()
        self.createQuads()
        self.createWeaponList()
        self.createComponentList()
        self.createDesignInfo()
        self.createDesignNameEntry()
        self.createDesignSubmit()
    
    def createDesignNameEntry(self):
        self.designNameEntry = textentry.TextEntry(self.path, self.mode, command='onDesignNameEntered',
                                                   initialText=self.mode.designName,
                                                   title='Enter Drone Design Name:', lines=1, width=18, 
                                                   x=0.7, z=0.11)
        self.myWidgets.append(self.designNameEntry)
    
    def createQuads(self):
        """Create the 4 Quadrant lists displaying design component info"""
        for (quad, (x,z)) in {'fore':(0.03,0.5)}.iteritems():
            text = self.getTextFromQuad(quad)
            setattr(self, '%sQuadInfo' % quad, buttonlist.ButtonList(self.path, text, width=0.6, height=0.50))
            myQuad = getattr(self, '%sQuadInfo' % quad)
            myQuad.setMyPosition(x,z)
            myQuad.setMyMode(self)
            myQuad.setOnClickMethod('%sQuadClicked' % quad)
            self.myWidgets.append(myQuad)
            self.populateQuadInfo(quad)
    
    def clearOtherQuads(self, quad):
        for name in ['fore']:
            if name != quad:
                myQuadList = getattr(self, '%sQuadInfo' % name)
                myQuadList.myScrolledList.restoreNodeButton2Normal()
        self.componentlist.myScrolledList.restoreNodeButton2Normal()
        self.weaponlist.myScrolledList.restoreNodeButton2Normal()
    
    def componentListClicked(self, id, index, button):
        self.clearOtherQuads('')
        self.createShipDesignValue(id)
        self.designSubmit.disableButton('removedesign')
        self.shipdesignvalue.pressZ()
        self.shipdesignvalue.disableButton('X')
        self.shipdesignvalue.disableButton('C')
        self.shipdesignvalue.disableButton('V')
    
if __name__ == "__main__":
    from anw.func import storedata
    data = storedata.loadFromFile('../../../Client/client.data')
    shiphulldata = data['shiphulldata']
    
    mediaPath = 'media'
    for i in range(1,22):
        id = str(i)
        myShipHull = shiphulldata[id]
        shiphull = ShipHull(mediaPath, None, '1', myShipHull)
    run()