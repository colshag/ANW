# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipdesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a starship design
# ---------------------------------------------------------------------------
import copy
import string

from anw.func import datatype, funcs, globals
import component
import quad
import weapon

class ShipDesign(datatype.DataType):
    """A StarShip Design contains quads, components, and weapons"""
    def __init__(self, args):
        # Attributes
        datatype.DataType.__init__(self, args)
        self.shipHullID = str() # ship hull type (id)
        self.maxBattery = float() # max battery power available
        self.maxPower = float() # max power available
        self.mass = float() # ship design total mass
        self.thrust = float() # ship thrust
        self.rotation = float() # ship rotation thrust
        self.radar = int() # ship radar
        self.jamming = int() # ship jamming
        self.repair = int() # repair points
        self.maxAssault = int() # max marine assault strength
        self.obsolete = int() # 1 = obsolete design
        self.accel = float() # current max acceleration of ship
        self.totalAMSPower = float() #total power draw of AMS Weapons
        self.totalWeapPower = float() #total power draw of Weapons
        self.amsFireRate = float() #total time to fire AMS weapons
        self.weapFireRate = float() #total time to fire Weapons
        self.hasAllTech = int() # 0=design past tech level of empire
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'shipHullID', 'maxBattery', 'maxPower', 'mass',
                                  'thrust', 'rotation', 'radar', 'jamming', 'repair', 
                                  'maxAssault', 'obsolete', 'accel','totalAMSPower',
                                  'totalWeapPower','amsFireRate','weapFireRate')
        self.setAttributes(args)
        
        self.myEmpire = None # Actual Empire object that this Ship Design created by
        self.componentdata = None # referenced
        self.weapondata = None # referenced
        self.myShipHull = None # Ship Hull object used in design
        self.quads = {} # key='fore','aft','port','star', value = quad obj
    
    def addComponent(self, type, quad, weapon=''):
        """Add component to Ship Design"""
        try:
            myQuad = self.quads[quad]
            myComponentData = self.componentdata[type]
            if weapon == '':
                if self.myEmpire.techTree != None:
                    if self.myEmpire.techTree[myComponentData.techReq].complete == 0:
                        self.hasAllTech = 0
            # first check if component space is available
            if myQuad.currentComps == self.myShipHull.componentNum:
                return 'You do not have enough slots to add component to %s Quadrant' % quad
            elif (myComponentData.abr in globals.componentLimitations[self.myShipHull.function] or 
                  (myComponentData.abr in ['CSE','CRT'] and self.myShipHull.id not in ['8','9','10','11','12'] )):
                return '%s cannot be added to %s' % (myComponentData.name, self.myShipHull.name)
            elif myComponentData.typeAP != '':
                # check if trying to add armor to quadrant that has armor of different type
                for id, myComponent in myQuad.components.iteritems():
                    if myComponent.myComponentData.typeAP != myComponentData.typeAP and myComponent.myComponentData.typeAP != '':
                        return 'You cannot add %s armor to a Quadrant with %s armor in it' % (myComponentData.typeAP, myComponent.myComponentData.typeAP)
            # create component
            id = myQuad.getNextID(myQuad.components)
            myComponent = component.Component({'id':id, 'type':type, 'weaponID':weapon})
            myComponent.setMyQuad(myQuad)
            myQuad.currentComps += 1
            return 1
        except:
            return 'addComponent-> error'
    
    def addWeapon(self, type, quad, facing, dronedesign=''):
        """Add weapon to Ship Design"""
        try:
            facing = facing % 360
            myQuad = self.quads[quad]
            myWeaponData = self.weapondata[type]
            if self.myEmpire.techTree != None:
                if self.myEmpire.techTree[myWeaponData.techReq].complete == 0:
                    self.hasAllTech = 0
            # first check if weapon space is available
            if (myQuad.currentComps + myWeaponData.numComps) > self.myShipHull.componentNum:
                return 'You do not have enough room to add weapon to %s Quadrant' % quad
            elif myWeaponData.abr in globals.weaponLimitations[self.myShipHull.function]:
                return '%s cannot be added to %s' % (myWeaponData.name, self.myShipHull.name)

            # create weapon
            id = myQuad.getNextID(myQuad.weapons)
            myWeapon = weapon.Weapon({'id':id, 'type':type, 'facing':facing, 'droneID':dronedesign})
            myWeapon.setMyQuad(myQuad)
            
            # add components that are part of weapon
            i = 1
            while i <= myWeaponData.numComps:
                result = self.addComponent(globals.weaponComponent, quad, id)
                if result != 1:
                    return result
                i += 1

            return 1
        except:
            return 'addWeapon-> error'
    
    def clearMyStatus(self):
        """Clear Ship Design Attributes"""
        self.abr = ''
        self.costCR = 0.0
        self.costAL = 0.0
        self.costEC = 0.0
        self.costIA = 0.0
        self.maxBattery = 0.0
        self.maxPower = 0.0
        self.thrust = 0.0
        self.rotation = 0.0
        self.radar = 0
        self.jamming = 0
        self.repair = 0
        self.mass = 0.0
        self.maxAssault = 0
        self.accel = 0.0
        self.hasAllTech = 1
    
    def getMyShipDesignInfo(self):
        """Return Ship Design info as dict"""
        d = self.getMyInfoAsDict()
        d['quads'] = self.getMyDictInfo('quads', 'getMyQuadInfo')
        return d
    
    def getImageFileName(self):
        """Return the ship design image filename"""
        return '%s_%s_%s' % (string.lower(self.myShipHull.abr), self.myEmpire.color1, self.myEmpire.color2)
    
    def getMyDesign(self):
        """Return the ship design attributes in the form of (hullID, compDict, weaponDict)"""
        compDict = {}
        weaponDict = {}
        hullID = self.myShipHull.id
        for position, myQuad in self.quads.iteritems():
            compList = []
            for compID, myComponent in myQuad.components.iteritems():
                # check if it is a weapon component
                if myComponent.weaponID != '':
                    compList.append('W%s' % myComponent.weaponID)
                else:
                    # its a regular component
                    compList.append(myComponent.type)
            compList.sort()
            compDict[position] = compList
            d = {}
            for weaponID, myWeapon in myQuad.weapons.iteritems():
                key = '%s-%s' % (position, weaponID)
                d = {'id':myWeapon.id, 'type':myWeapon.type, 'facing':myWeapon.facing}
                if myWeapon.droneID != '':
                    d['dronedesign'] = myWeapon.droneID
                weaponDict[key] = d
        return (self.name, hullID, compDict, weaponDict)

    def setWeaponRates(self):
        """Calculate the AMS and Weapon Power and Fire Rates"""
        self.totalAMSPower = 0.0
        self.totalWeapPower = 0.0
        self.amsFireRate = 0.0
        self.weapFireRate = 0.0
        for position, myQuad in self.quads.iteritems():
            for weaponID, myWeapon in myQuad.weapons.iteritems():
                if myWeapon.myWeaponData.AMS == 1:
                    self.totalAMSPower += myWeapon.myWeaponData.maxPower
                else:
                    self.totalWeapPower += myWeapon.myWeaponData.maxPower
        
        if self.maxPower:
            self.amsFireRate = self.totalAMSPower/self.maxPower
            self.weapFireRate = self.totalWeapPower/self.maxPower

    def getSYCRequired(self):
        """Return the amount of Shipyard Capacity Points required to build this design"""
        return int(self.myShipHull.componentNum)*8
    
    def getUpgradeCost(self, newDesign):
        """Get the upgrade cost of Starship Design"""
        if newDesign.myShipHull != self.myShipHull:
            return 'Ship Hulls are different'
        CR = 0
        AL = 0
        EC = 0
        IA = 0
        totalSlots = self.myShipHull.componentNum*4
        upgradeSlots = 0
        
        # compare to ship design, add costs of replacement
        for position, newQuad in newDesign.quads.iteritems():
            myQuad = self.quads[position]
            weaponsInQuad = []           
            # go through components
            for componentID, newComponent in newQuad.components.iteritems():
                missingComponent = 0
                if componentID in myQuad.components.keys():
                    myComponent = myQuad.components[componentID]
                    if myComponent.myComponentData.id != newComponent.myComponentData.id:
                        missingComponent = 1
                else:
                    missingComponent = 1
                if missingComponent == 1:
                    upgradeSlots += 1
                    if newComponent.weaponID == '':
                        # regular component
                        CR += newComponent.myComponentData.costCR
                        AL += newComponent.myComponentData.costAL
                        EC += newComponent.myComponentData.costEC
                        IA += newComponent.myComponentData.costIA
                    elif newComponent.weaponID not in weaponsInQuad:
                        # component part of weapon, weapon must be replaced
                        weaponsInQuad.append(newComponent.weaponID)
                        
            # go through weapons that need to be taken care of in upgrade
            for weaponID in weaponsInQuad:
                newWeapon = newQuad.weapons[weaponID]
                CR += newWeapon.myWeaponData.costCR
                AL += newWeapon.myWeaponData.costAL
                EC += newWeapon.myWeaponData.costEC
                IA += newWeapon.myWeaponData.costIA
        
        capacityRequired = int(self.getSYCRequired() * float(upgradeSlots)/float(totalSlots))
        
        return [CR,AL,EC,IA,capacityRequired]
    
    def setMyDesign(self, hullID, compDict, weaponDict):
        """Taking the standard input required, create a full ship design,
        compDict = {'fore':['23','34','54','54'], 'port':['W1','W1','W1',W1'], etc..
        weapDict = {'fore-1':{'id':'3', 'type':'4', 'facing':0}..."""
        try:
            weaponDict = copy.copy(weaponDict)
            self.setMyShipHull(hullID)
            result = 1
            # build components
            for position, compTypesList in compDict.iteritems():
                # create quad
                myQuad = quad.Quad({'position':position})
                myQuad.setMyParent(self)
                # add components
                i = 1
                while i <= len(compTypesList):
                    type = compTypesList[i-1]
                    # check for weapon component
                    if type[0] == 'W':
                        weaponID = type[1:]
                        weaponKey = '%s-%s' % (position, weaponID)
                        if weaponDict.has_key(weaponKey):
                            # weapon has not been added yet
                            d = weaponDict[weaponKey]
                            if d.has_key('dronedesign'):
                                dronedesign = d['dronedesign']
                            else:
                                dronedesign = ''
                            result = self.addWeapon(d['type'], position, d['facing'], dronedesign)
                            if result != 1:
                                return result
                            del weaponDict[weaponKey]
                    else:
                        # not a weapon component
                        result = self.addComponent(type, position)
                        if result != 1:
                            return result
                    
                    i += 1
    
                myQuad.resetDefences()
            
            # set the ship designs attributes now that all components/weapons in place
            self.setMyStatus()
            return result
        except:
            return 'shipdesign->setMyDesign error'
    
    def setMyEmpire(self, empireObject):
        """Set the Ship Empire Owner"""
        self.myEmpire = empireObject
        empireObject.shipDesigns[self.id] = self
        self.weapondata = self.myEmpire.myGalaxy.weapondata
        self.componentdata = self.myEmpire.myGalaxy.componentdata
    
    def setMyShipHull(self, hullID):
        """Set the ship hull for this design"""
        self.shipHullID = hullID
        self.myShipHull = self.myEmpire.myGalaxy.shiphulldata[self.shipHullID]
        if self.myEmpire.techTree != None:
            if self.myEmpire.techTree != {}:
                if self.myEmpire.techTree[self.myShipHull.techReq].complete == 0:
                    self.hasAllTech = 0
        
    def setMyStatus(self):
        """Set the status of all calculated attributes"""
        # abr is related to the type of weapons on the design, plus hull type
        self.clearMyStatus()
        self.setMyShipHull(self.shipHullID)
        self.abr = self.myShipHull.abr
        self.mass = self.myShipHull.mass
        
        # hull
        self.costCR += self.myShipHull.costCR
        self.costAL += self.myShipHull.costAL
        self.costEC += self.myShipHull.costEC
        self.costIA += self.myShipHull.costIA
        
        for quad in self.quads.keys():
            myQuad = self.quads[quad]
            myQuad.setMyStatus()
            self.maxBattery += myQuad.maxBattery
            self.maxPower += myQuad.maxPower
            self.thrust += myQuad.thrust
            self.rotation += myQuad.rotation
            self.radar += myQuad.radar
            self.jamming += myQuad.jamming
            self.repair += myQuad.repair
            self.abr = self.abr + '-'
            self.mass += myQuad.mass
            self.maxAssault += myQuad.maxAssault
            # weapons
            weaponKeys = funcs.sortStringList(self.quads[quad].weapons.keys())
            for key in weaponKeys:
                myWeapon = myQuad.weapons[key]
                myWeaponData = self.weapondata[myWeapon.type]
                if self.myEmpire.techTree != None:
                    if self.myEmpire.techTree[myWeaponData.techReq].complete == 0:
                        self.hasAllTech = 0
                self.abr = self.abr + myWeaponData.abr + str(int(myWeapon.facing))
                if myWeapon.droneID != '':
                    myDroneDesign = self.myEmpire.droneDesigns[myWeapon.droneID]
                    self.costCR += myDroneDesign.costCR
                    self.costAL += myDroneDesign.costAL
                    self.costEC += myDroneDesign.costEC
                    self.costIA += myDroneDesign.costIA
                    if myDroneDesign.hasAllTech == 0:
                        self.hasAllTech = 0
                
                self.costCR += myWeaponData.costCR
                self.costAL += myWeaponData.costAL
                self.costEC += myWeaponData.costEC
                self.costIA += myWeaponData.costIA
            
            # components
            for compID, myComp in myQuad.components.iteritems():
                if myComp.type != '':
                    myCompData = self.componentdata[myComp.type]
                    if myCompData.name != 'Weapon Component':
                        if self.myEmpire.techTree != None:
                            if self.myEmpire.techTree[myCompData.techReq].complete == 0:
                                self.hasAllTech = 0
                    self.costCR += myCompData.costCR
                    self.costAL += myCompData.costAL
                    self.costEC += myCompData.costEC
                    self.costIA += myCompData.costIA
        
        self.accel = self.getAccel(self.thrust, self.mass)
        self.rotation = self.getRotation(self.rotation, self.mass)
        self.setWeaponRates()
        
    def getMyBattleValue(self):
        """Return Battle Value of Ship Design"""
        valueBV = 0.0
        valueCR = 0.0
        valueAL = 0.0
        valueEC = 0.0
        valueIA = 0.0
        factorAL = globals.cityCRGen/globals.cityALGen
        factorEC = globals.cityCRGen/globals.cityECGen
        factorIA = globals.cityCRGen/globals.cityIAGen
        ratio = 1
        valueCR += self.costCR*ratio
        valueAL += self.costAL*ratio
        valueEC += self.costEC*ratio
        valueIA += self.costIA*ratio
        valueBV += (valueCR +
                    valueAL*factorAL +
                    valueEC*factorEC +
                    valueIA*factorIA) / 1000.0
        return valueBV
        
    def getAccel(self, thrust, mass):
        """Return Ship Accel
        # F=ma, F=thrust = MegaNeutons, accel = F/ship mass
        """
        self.accel = thrust*1000.0/mass
        self.limitAccel()
        self.accel = round(self.accel,2)
        return self.accel
    
    def getRotation(self, rotation, mass):
        """Return Ship Rotation"""
        self.rotation = rotation*32000.0/mass
        self.limitRotation()
        self.rotation = round(self.rotation,2)
        return self.rotation
    
    def limitAccel(self):
        if self.accel > globals.maxAccel:
            self.accel = globals.maxAccel
    
    def limitRotation(self):
        if self.rotation > globals.maxRotation:
            self.rotation = globals.maxRotation
            