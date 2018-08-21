# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipdesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a starship design
# ---------------------------------------------------------------------------
import copy
import string

import anwp.func.datatype
import anwp.func.funcs
import anwp.func.globals
import anwp.war.component
import anwp.war.quad
import anwp.war.weapon

class ShipDesign(anwp.func.datatype.DataType):
    """A StarShip Design contains quads, components, and weapons"""
    def __init__(self, args):
        # Attributes
        anwp.func.datatype.DataType.__init__(self, args)
        self.shipHullID = str() # ship hull type (id)
        self.maxBattery = float() # max battery power available
        self.maxPower = float() # max power available
        self.mass = float() # ship design total mass
        self.thrust = float() # ship thrust
        self.rotation = float() # ship rotation thrust
        self.radar = int() # ship radar
        self.jamming = int() # ship jamming
        self.repair = int() # repair points
        self.maxTransport = int() # max transport of ship in regiments
        self.obsolete = int() # 1 = obsolete design
        self.accel = float() # current max acceleration of ship
        
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'shipHullID', 'maxBattery', 'maxPower', 'mass',
                                  'thrust', 'rotation', 'radar', 'jamming', 'repair', 
                                  'maxTransport', 'obsolete', 'accel')
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
            # first check if component space is available
            if myQuad.currentComps == self.myShipHull.componentNum:
                return 'You do not have enough slots to add component to %s Quadrant' % quad
            elif myComponentData.abr in anwp.func.globals.componentLimitations[self.myShipHull.function]:
                return '%s cannot be added to %s' % (myComponentData.name, self.myShipHull.name)
            elif myComponentData.typeAP <> '':
                # check if trying to add armor to quadrant that has armor of different type
                for id, myComponent in myQuad.components.iteritems():
                    if myComponent.myComponentData.typeAP <> myComponentData.typeAP and myComponent.myComponentData.typeAP <> '':
                        return 'You cannot add %s armor to a Quadrant with %s armor in it' % (myComponentData.typeAP, myComponent.myComponentData.typeAP)
            # create component
            id = myQuad.getNextID(myQuad.components)
            myComponent = anwp.war.component.Component({'id':id, 'type':type, 'weaponID':weapon})
            myComponent.setMyQuad(myQuad)
            myQuad.currentComps += 1
            return 1
        except:
            return 'addComponent-> error'
    
    def addWeapon(self, type, quad, facing, dronedesign):
        """Add weapon to Ship Design"""
        try:
            facing = facing % 360
            myQuad = self.quads[quad]
            myWeaponData = self.weapondata[type]
            # first check if weapon space is available
            if (myQuad.currentComps + myWeaponData.numComps) > self.myShipHull.componentNum:
                return 'You do not have enough room to add weapon to %s Quadrant' % quad
            elif myWeaponData.abr in anwp.func.globals.weaponLimitations[self.myShipHull.function]:
                return '%s cannot be added to %s' % (myWeaponData.name, self.myShipHull.name)
            
            # check if drone design is valid
            if dronedesign <> '':
                myDroneDesign = self.myEmpire.droneDesigns[dronedesign]
                if myWeaponData.numComps < myDroneDesign.myShipHull.componentNum:
                    return 'Your drone launcher bay is not big enough for the drone you wish to place in it'
            
            # create weapon
            id = myQuad.getNextID(myQuad.weapons)
            myWeapon = anwp.war.weapon.Weapon({'id':id, 'type':type, 'facing':facing, 'droneID':dronedesign})
            myWeapon.setMyQuad(myQuad)
            
            # add components that are part of weapon
            i = 1
            while i <= myWeaponData.numComps:
                result = self.addComponent(anwp.func.globals.weaponComponent, quad, id)
                if result <> 1:
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
        self.maxTransport = 0
        self.accel = 0.0
    
    def getMyShipDesignInfo(self):
        """Return Ship Design info as dict"""
        d = self.getMyInfoAsDict()
        d['quads'] = self.getMyDictInfo('quads', 'getMyQuadInfo')
        return d
    
    def getImageFileName(self):
        """Return the ship design image filename"""
        return '%s_%s_%s' % (string.lower(self.myShipHull.abr), self.myEmpire.color1, self.myEmpire.color2)
    
    def getMyDesign(self):
        """Return the design attributes in the form of (hullID, compDict, weaponDict)"""
        compDict = {}
        weaponDict = {}
        hullID = self.myShipHull.id
        for position, myQuad in self.quads.iteritems():
            compList = []
            for compID, myComponent in myQuad.components.iteritems():
                # check if it is a weapon component
                if myComponent.weaponID <> '':
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
                weaponDict[key] = d
        return (self.name, hullID, compDict, weaponDict)
    
    def getMyDesignName(self):
        """Return the Design name minus the user specifix suffix"""
        designName = '%s%s-' % (self.myShipHull.abr, self.id)
        return designName

    def getSYCRequired(self):
        """Return the amount of Shipyard Capacity Points required to build this design"""
        return int(self.myShipHull.componentNum)*8
    
    def getUpgradeCost(self, newDesign):
        """Get the upgrade cost of Starship Design"""
        if newDesign.myShipHull <> self.myShipHull:
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
                    if myComponent.myComponentData.id <> newComponent.myComponentData.id:
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
                myQuad = anwp.war.quad.Quad({'position':position})
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
                            if result <> 1:
                                return result
                            del weaponDict[weaponKey]
                    else:
                        # not a weapon component
                        result = self.addComponent(type, position)
                        if result <> 1:
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
        try:
            self.myShipHull = self.myEmpire.myGalaxy.shiphulldata[self.shipHullID]
        except:
            pass
        
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
            self.maxTransport += myQuad.maxTransport
            # weapons
            weaponKeys = anwp.func.funcs.sortStringList(self.quads[quad].weapons.keys())
            for key in weaponKeys:
                myWeapon = myQuad.weapons[key]
                myWeaponData = self.weapondata[myWeapon.type]
                self.abr = self.abr + myWeaponData.abr + str(int(myWeapon.facing))
                self.costCR += myWeaponData.costCR
                self.costAL += myWeaponData.costAL
                self.costEC += myWeaponData.costEC
                self.costIA += myWeaponData.costIA
            
            # components
            for compID, myComp in myQuad.components.iteritems():
                if myComp.type <> '':
                    myCompData = self.componentdata[myComp.type]
                    self.costCR += myCompData.costCR
                    self.costAL += myCompData.costAL
                    self.costEC += myCompData.costEC
                    self.costIA += myCompData.costIA
                    
        # accel
        self.accel = self.getAccel(self.thrust, self.mass)
                
        # rotation
        self.rotation = self.getRotation(self.rotation, self.mass)
        
    def getAccel(self, thrust, mass):
        """Return Ship Accel
        # F=ma, F=thrust = MegaNeutons, accel = F/ship mass
        """
        accel = thrust*1000000.0/mass
        if accel > anwp.func.globals.maxAccel:
            accel = anwp.func.globals.maxAccel
        return accel
    
    def getRotation(self, rotation, mass):
        """Return Ship Rotation"""
        rotation = rotation*32000/mass
        if rotation > anwp.func.globals.maxRotation:
            rotation = anwp.func.globals.maxRotation
        return rotation
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_shipdesign.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        