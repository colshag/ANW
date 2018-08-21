# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# industrydata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for industry, industry objects will reference this object
# ---------------------------------------------------------------------------
from anw.func import datatype

class IndustryData(datatype.DataType):
    """A Industry Data object represents one type of Industry in detail"""
    def __init__(self, args):
        # Attributes
        datatype.DataType.__init__(self, args)
        self.cities = int() # number of cities required to run industry
        self.output = float() # output of industry
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'cities', 'output')
        self.setAttributes(args)
        