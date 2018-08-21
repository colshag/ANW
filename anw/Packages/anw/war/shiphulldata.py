# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shiphulldata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for ship hulls, ship design objects will reference this object
# ---------------------------------------------------------------------------
from anw.func import datatype, globals

class ShipHullData(datatype.DataType):
    """A Weapon Data object represents one type of Weapon in detail"""
    def __init__(self, args):
        # Attributes
        datatype.DataType.__init__(self, args)
        self.function = str() # 'platform', 'carrier', 'assault', 'warship'
        self.size = str() # size of ship, 'tiny', 'small', 'large'
        self.componentNum = int() # number of components per quadrant
        self.maxISP = float() # max internal structure points
        self.mass = float() # default mass of hull
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'function', 'size', 'componentNum', 'maxISP', 'mass')
        self.setAttributes(args)
        self.hardPoints = {}
        self.setHardpoints()
    
    def setHardpoints(self):
        """Set the hardpoints for hull"""
        if self.abr != '':
            self.hardPoints = globals.hardPoints[self.abr] # represents a ship hulls hard points
    
class DroneHullData(ShipHullData):
    """Drones"""
    
    def setHardpoints(self):
        """Set the hardpoints for drone hulls"""
        self.hardPoints = {'fore-1':[0,0], 'fore-2':[90,5], 'fore-3':[180,5], 'fore-4':[270,5]}
