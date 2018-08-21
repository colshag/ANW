# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# dronedesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a drone design
# ---------------------------------------------------------------------------
import copy
import string

from anw.war import shipdesign
from anw.func import globals

class DroneDesign(shipdesign.ShipDesign):
    """A Drone Design contains components, and weapons, only has one quadrant fore"""
    def __init__(self, args):
        # Attributes
        shipdesign.ShipDesign.__init__(self, args)
    
    def getMyDroneDesignInfo(self):
        """Return Drone Design info as dict"""
        d = self.getMyInfoAsDict()
        d['quads'] = self.getMyDictInfo('quads', 'getMyQuadInfo')
        return d
    
    def setMyEmpire(self, empireObject):
        """Set the Drone Design Empire Owner"""
        self.myEmpire = empireObject
        empireObject.droneDesigns[self.id] = self
        self.weapondata = self.myEmpire.myGalaxy.weapondata
        self.componentdata = self.myEmpire.myGalaxy.componentdata
    
    def setMyShipHull(self, hullID):
        """Set the ship hull for this design"""
        self.shipHullID = hullID
        self.myShipHull = self.myEmpire.myGalaxy.dronehulldata[self.shipHullID]
        if self.myEmpire.techTree != None:
            if self.myEmpire.techTree[self.myShipHull.techReq].complete == 0:
                self.hasAllTech = 0
    
    def getMyLauncherID(self):
        """Get the Drone Launcher ID"""
        for id, myWeaponData in self.weapondata.iteritems():
            if (myWeaponData.abr[:2] == self.myShipHull.abr[:2] and
                myWeaponData.abr[2:] == 'L'):
                return id
    
    def getAccel(self, thrust, mass):
        """Return Ship Accel
        # F=ma, F=thrust = MegaNeutons, accel = F/ship mass
        """
        self.accel = globals.droneAccel
        return self.accel
    
    def getRotation(self, rotation, mass):
        """Return Ship Rotation"""
        self.rotation = globals.droneRotation
        return self.rotation
    