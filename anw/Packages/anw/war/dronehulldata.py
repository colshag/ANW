# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# dronehulldata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for drone hulls, drone design objects will reference this object
# ---------------------------------------------------------------------------
from anw.war import shiphulldata

class DroneHullData(shiphulldata.ShipHullData):
    """This is a data container for drone hulls"""
    
    def setHardpoints(self):
        """Set the hardpoints for drone hulls"""
        self.hardPoints = {'fore-1':[0,0], 'fore-2':[90,5], 'fore-3':[180,5], 'fore-4':[270,5]}
