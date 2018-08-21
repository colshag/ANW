# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays Ship Information
# ---------------------------------------------------------------------------
import string

from anw.gui import designinfo, textonscreen, valuebar
from anw.func import globals, funcs

class ShipInfo(designinfo.DesignInfo):
    """Describe Ship Info"""
    def __init__(self, path, myShip, x, y):
        self.myShip = myShip
        designinfo.DesignInfo.__init__(self, path, myShip.empireID, myShip.myDesign, x, y)
        self.shipinfo = []
        self.quadinfo = []
        self.weapinfo = []
        self.setMyChangingAttributes()
        self.textCaptain = None
        self.myEmpire = self.myShip.myGalaxy.empires[self.myShip.empireID]
        self.myTitle.setText('(%s)(%s) Status:' % (self.myEmpire.name, self.myShip.name))
        self.writeAttributes()
    
    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode
        
    def createSim(self, x=0.1, y=-0.1):
        designinfo.DesignInfo.createSim(self, 0.1, -0.15)
    
    def setMyChangingAttributes(self):
        """Setup all attributes that can change when ship is in simulation"""
        self.shipinfo = [['shipISP', self.myShip.currentISP, self.myShip.myDesign.myShipHull.maxISP, 'STRUCTURE'],
                ['shipStrength', self.myShip.strength, 100.0, '% STRENGTH'],
                ['shipAccel', self.myShip.accel, self.myShip.myDesign.accel, 'THRUST'],
                ['shipRotation', self.myShip.rotation, self.myShip.myDesign.rotation, 'ROTATION'],
                ['shipPower', self.myShip.currentPower, self.myShip.myDesign.maxPower, 'POWER'],
                ['shipBattery', self.myShip.currentBattery, self.myShip.maxBattery, 'BATTERY'],
                ['maxAssault', self.myShip.maxAssault, self.myShip.myDesign.maxAssault, 'MARINE ASSAULT']
               ]
        
        self.quadinfo = []
        for position in self.myShip.positions:
            if position in self.myShip.quads.keys():
                shipQuad = self.myShip.quads[position]
                designQuad = self.myShip.myDesign.quads[position]
                self.quadinfo.append([position+'Shields', shipQuad.currentSP, designQuad.maxSP, '%s SHIELDS' % string.upper(position)])
                self.quadinfo.append([position+'Armor', shipQuad.currentAP, designQuad.maxAP, '%s ARMOR' % string.upper(position)])
                self.quadinfo.append([position+'Comps', shipQuad.currentComps, self.myShip.myDesign.myShipHull.componentNum, '%s COMPONENTS' % string.upper(position)])
            
                for id in funcs.sortStringList(shipQuad.weapons.keys()):
                    myWeapon = shipQuad.weapons[id]
                    self.weapinfo.append(['%sweapon%sStatus' % (position,id), myWeapon.operational, 1, myWeapon.myWeaponData.name])
                    self.weapinfo.append(['%sweapon%sLock' % (position,id), myWeapon.currentLock, myWeapon.maxLock, 'LOCK'])
                    self.weapinfo.append(['%sweapon%sPower' % (position,id), myWeapon.currentPower, myWeapon.myWeaponData.maxPower, 'POWER'])
                    if myWeapon.droneID != '':
                        self.weapinfo.append(['%sweapon%sAmmo' % (position,id), 1, 1, 'DRONE LAUNCH'])
                    elif myWeapon.myWeaponData.ammo == 0:
                        self.weapinfo.append(['%sweapon%sAmmo' % (position,id), 1, 1, 'UNLIMITED AMMO'])
                    else:
                        self.weapinfo.append(['%sweapon%sAmmo' % (position,id), myWeapon.availAmmo, myWeapon.availAmmo, 'AMMO'])
                     
        self.createAttributes(self.shipinfo)
        self.createAttributes(self.quadinfo)
        self.createAttributes(self.weapinfo)
    
    def createAttributes(self, attrs):
        for attr in attrs:
            if attr[2] > 0:
                setattr(self, attr[0], None)
    
    def writeAttributes(self):
        """For Each Attribute given display"""
        self.yOffset -= 0.02
        self.writeAttribute(self.textCaptain, 1, 'guiwhite', self.myShip.myCaptain.fullName)
        self.writeAttribute(self.textTotalAMSPower, 1, 'guigreen','AMS Power = %d' % self.myDesign.totalAMSPower, x=0.22)
        self.writeAttribute(self.textTotalWeapPower, 1, 'guigreen','Weap Power = %d' % self.myDesign.totalWeapPower, x=0.22)
        self.writeAttribute(self.textAMSFireRate, 1, 'guigreen','AMS Fire Rate = %.2f' % self.myDesign.amsFireRate, x=0.22)
        self.writeAttribute(self.textWeapFireRate, 1, 'guigreen','Weap Fire Rate = %.2f' % self.myDesign.weapFireRate, x=0.22)
        
        self.writeShipAttributes()
        self.writeQuadAttributes()
        self.writeWeaponAttributes()
    
    def writeShipAttributes(self):
        count = 0
        for (name, currentValue, maxValue, text) in self.shipinfo:
            if count%2 > 0:
                x = 0.48
                self.yOffset += 0.04
            else:
                x = 0
            self.writeChangingAttribute(name, currentValue, maxValue, text, x)
            count += 1
        self.yOffset -= 0.06
        
    def writeQuadAttributes(self):
        yCount = 0
        for (name, currentValue, maxValue, text) in self.quadinfo:
            x = 0.24
            if 'port' in name:
                x = 0
                yCount += 1
            elif 'star' in name:
                x = 0.48
            if name == 'starShields':
                self.yOffset += 0.04*yCount
            self.writeChangingAttribute(name, currentValue, maxValue, text, x)
            
    def writeWeaponAttributes(self):
        count = 1
        for (name, currentValue, maxValue, text) in self.weapinfo:
            if 'Status' in name:
                count += 1
                self.yOffset -= 0.02
            if count%2 > 0:
                x = 0.48
                if 'Status' in name:
                    self.yOffset += 0.18
            else:
                x = 0
            self.writeChangingAttribute(name, currentValue, maxValue, text, x)
        
    def writeChangingAttribute(self, name, currentValue, maxValue, text, x=0):
        """Write the changing attribute as a bar value"""
        if currentValue > maxValue:
            currentValue = maxValue
        if name in ['shipAccel','shipRotation'] or 'Lock' in name:
            decimal = 1
        else:
            decimal = 0
            
        self.yOffset -= 0.04
        setattr(self, name, (valuebar.ValueBar(self.path, scale=0.25, extraText=text, decimal=decimal, showOverValues=0)))
        myAttr = getattr(self, name)
        myAttr.setMyValues(currentValue, maxValue)
        myAttr.setMyPosition(self.posInitX+x+0.15, 0, self.posInitY+self.yOffset)
        myAttr.setColor(funcs.getDamageColor(currentValue, maxValue))
        myAttr.myBar.setSx(0.23)
        self.myWidgets.append(myAttr)
    
    def updateAttributes(self, dAttrs):
        """Update attributes given a dict of attribute name, and currentvalue"""
        for name, currentValue in dAttrs.iteritems():
            if hasattr(self, name):
                myAttr = getattr(self, name)
                if myAttr.currentValue != currentValue:
                    myAttr.setMyValues(currentValue, myAttr.maxValue)
                    myAttr.setColor(funcs.getDamageColor(currentValue, myAttr.maxValue))
                