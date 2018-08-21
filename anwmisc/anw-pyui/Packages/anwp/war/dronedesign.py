# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# dronedesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a drone design
# ---------------------------------------------------------------------------
import copy
import string

import anwp.war.shipdesign

class DroneDesign(anwp.war.shipdesign.ShipDesign):
    """A Drone Design contains components, and weapons, only has one quadrant fore"""
    def __init__(self, args):
        # Attributes
        anwp.war.shipdesign.ShipDesign.__init__(self, args)
    
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
        try:
            self.myShipHull = self.myEmpire.myGalaxy.dronehulldata[self.shipHullID]
        except:
            pass
        
    def getAccel(self, thrust, mass):
        """Return Ship Accel
        # F=ma, F=thrust = MegaNeutons, accel = F/ship mass
        """
        accel = thrust*1000000.0/mass
        if accel > anwp.func.globals.maxDroneAccel:
            accel = anwp.func.globals.maxDroneAccel
        return accel
    
    def getRotation(self, rotation, mass):
        """Return Ship Rotation"""
        rotation = rotation*32000/mass
        if rotation > anwp.func.globals.maxDroneRotation:
            rotation = anwp.func.globals.maxDroneRotation
        return rotation
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_dronedesign.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        