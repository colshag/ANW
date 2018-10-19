# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# quad.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a ship quadrant
# ---------------------------------------------------------------------------
from anw.func import root, globals, funcs

class Quad(root.Root):
    """A Ship has 4 quadrants, fore, aft, port, starboard"""
    def __init__(self, args):
        # Attributes
        self.position = str() # 'fore', 'aft', 'port', 'star'
        self.currentSP = int() # current shield points
        self.maxSP = int() # max shield points, calculated
        self.genSP = int() # generated shield points, calculated
        self.target = float() # the cumulative percentage bonus to target lock times
        self.currentAP = int() # current armor points
        self.currentComps = int() # current components being used in quad
        self.maxAP = int() # max armor points, calculated
        self.typeAP = str() # '', 'energy', 'impact'
        self.maxBattery = float() # max battery power available
        self.maxPower = float() # max power available
        self.mass = float() # current mass of quadrant
        self.thrust = float() # quad thrust addition
        self.rotation = float() # quad rotation addition
        self.radar = int() # quad radar
        self.jamming = int() # quad jamming
        self.repair = int() # quad repair
        self.maxAssault = int() # max space marine assault strength
        self.defaultAttributes = ('position', 'currentSP', 'maxSP', 'genSP', 'target',
                                  'currentAP', 'currentComps', 'maxAP', 'typeAP', 'maxBattery', 
                                  'maxPower', 'mass', 'thrust', 'rotation', 'radar', 'jamming', 'repair', 'maxAssault')
        self.setAttributes(args)
        
        self.components = {} # key=id, value=component obj
        self.weapons = {} # key=id, value=weapon obj
        self.myParent = None # parent is ship or shipdesign
        self.componentdata = None # Referenced
        self.weapondata = None # Referenced
    
    def clearMyStatus(self):
        """Clear Quad Attributes"""
        self.currentComps = 0
        self.maxSP = 0
        self.genSP = 0
        self.maxAP = 0
        self.typeAP = ''
        self.maxPower = 0
        self.maxBattery = 0
        self.thrust = 0
        self.rotation = 0
        self.radar = 0
        self.jamming = 0
        self.repair = 0
        self.mass = 0.0
        self.target = 0
        self.maxAssault = 0
            
    def getMyQuadInfo(self):
        """Return Quad info as dict"""
        d = self.getMyInfoAsDict()
        d['components'] = self.getMyDictInfo('components')
        d['weapons'] = self.getMyDictInfo('weapons')
        return d
    
    def setMyParent(self, parentObject):
        """Set the Ship Owner of this Quad"""
        self.myParent = parentObject
        self.myParent.quads[self.position] = self
        self.componentdata = parentObject.componentdata
        self.weapondata = parentObject.weapondata
    
    def setMyStatus(self):
        """Go through the components of Quad and set its general attributes"""
        self.clearMyStatus()
        for id, myComponent in self.components.iteritems():
            self.currentComps += 1
            if myComponent.type != '':
                compData = self.componentdata[myComponent.type]
                if myComponent.currentHP == myComponent.myComponentData.maxHP:
                    # regular component set quad Attributes
                    if compData.typeAP != '':
                        self.typeAP = compData.typeAP
                    elif compData.assault > 0:
                        self.maxAssault += compData.assault
                    self.maxAP += compData.maxAP
                    self.maxSP += compData.maxSP
                    self.genSP += compData.genSP
                    self.maxPower += compData.power
                    self.maxBattery += compData.battery
                    self.thrust += compData.engine
                    self.rotation += compData.rotate
                    self.radar += compData.radar
                    self.jamming += compData.jamming
                    self.repair += compData.repair
                    self.target += compData.target
                self.mass += compData.mass
        
        # tell weapons in quad to recalc their status
        for id, myWeapon in self.weapons.iteritems():
            myWeapon.setMyStatus()
    
    def reloadAmmo(self):
        """reload Ammo in any weapons in quad"""
        for componentID, myComponent in self.components.iteritems():
            if myComponent.myComponentData.maxAmmo > 0:
                myComponent.currentAmount = myComponent.myComponentData.maxAmmo
    
    def resetDefences(self):
        """Take the current max AP and SP and reset the current AP SP"""
        self.currentAP = self.maxAP
        self.currentSP = self.maxSP
    
    def regenShields(self, kW, kWtoSPfactor):
        """Regenerate Shields in Quadrant"""
        remainder = kW 
        if self.currentSP < self.maxSP:
            # how many kW required to fully charge?
            # desiredSP = kWneeded * fact
            # kWneeded = desiredSP/fact
            desiredSP = self.maxSP - self.currentSP
            kWneeded = desiredSP / kWtoSPfactor
            if kW > kWneeded:
                remainder = kW - kWneeded
                #print "more kW than need for sheilds; remainder",remainder
            else:
                remainder = 0
            
            self.currentSP += (kW * kWtoSPfactor)
            if self.currentSP > self.maxSP:
                self.currentSP = self.maxSP
            self.myParent.updateMyGUIValue(self.position+'Shields', self.currentSP)
        return remainder
    
    def takeHit(self, amount, type, enemyShip):
        """Quadrant takes a hit of type='impact', or 'energy'"""
        if type == 'energy':
            # go through shields in quadrant first
            if self.currentSP > 0:
                if self.currentSP >= amount:
                    self.currentSP -= amount
                    amount = 0
                else:
                    amount -= self.currentSP
                    self.currentSP = 0
            # go through armor next
            if self.currentAP > 0 and amount > 0:
                # set experience only if shot goes through shields
                if self.typeAP == 'energy':
                    if self.currentAP >= (amount * globals.reflectiveArmorModifier):
                        self.currentAP -= (amount * globals.reflectiveArmorModifier)
                        amount = 0
                    else:
                        amount -= (self.currentAP/globals.reflectiveArmorModifier)
                        self.currentAP = 0
                else:
                    if self.currentAP >= amount:
                        self.currentAP -= amount
                        amount = 0
                    else:
                        amount -= self.currentAP
                        self.currentAP = 0
        elif type == 'impact':
            # go through shields in quadrant first
            if self.currentSP > 0:
                if self.currentSP >= amount:
                    self.currentSP -= amount/2
                    amount = amount/2
                else:
                    amount -= self.currentSP
                    self.currentSP = 0
                    
            # now goto armor
            if self.currentAP > 0 and amount > 0:
                if self.typeAP == 'impact':
                    if self.currentAP >= (amount * globals.impactArmorModifier):
                        self.currentAP -= (amount * globals.impactArmorModifier)
                        amount = 0
                    else:
                        amount -= (self.currentAP/globals.impactArmorModifier)
                        self.currentAP = 0
                else:
                    if self.currentAP >= amount:
                        self.currentAP -= amount
                        amount = 0
                    else:
                        amount -= self.currentAP
                        self.currentAP = 0
        
        # now that shields and armor are taken care of transfer remaining damage to internal components
        self.myParent.setExperience(amount, enemyShip)
        componentDamage = 0
        if amount > 0 and self.components != {}:
            while amount > 0:
                keyList = funcs.sortStringList(self.components.keys())
                componentDamage = 1
                for componentID in keyList:
                    component = self.components[componentID]
                    if component.currentHP > amount:
                        component.currentHP -= amount
                        amount = 0
                        break
                    elif component.currentHP > 0:
                        # remove component
                        amount -= component.currentHP
                        del self.components[componentID]
                
                # check if all components destroyed, or damage absorbed
                if self.components == {} or amount == 0:
                    break
        
        if componentDamage == 1:
            self.setMyStatus()
            self.myParent.setMyStatus()
        
        if amount > 0:
            if self.myParent.currentISP > amount:
                self.myParent.currentISP -= amount
                self.myParent.setMyStatus()
                amount = 0
            else:
                self.myParent.destroyMe()
                amount = 0
            
        self.myParent.updateAllGUIValues()
        
