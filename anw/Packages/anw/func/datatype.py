# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# datatype.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the parent data type object of all data type objects
# ---------------------------------------------------------------------------
from anw.func import root

class DataType(root.Root):
    """A DataType contains one set of information stored at the galactic level 
    Objects reference these DataTypes instead of containing the information directly"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given Name
        self.abr = str() # abrievation
        self.costCR = float() # cost in credits
        self.costAL = float() # cost in alloys
        self.costEC = float() # cost in energy
        self.costIA = float() # cost in arrays
        self.techReq = str() # tech required
        self.description = str() # description of type
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description')
        self.setAttributes(args)
        