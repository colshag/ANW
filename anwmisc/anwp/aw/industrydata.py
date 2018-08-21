# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# industrydata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for industry, industry objects will reference this object
# ---------------------------------------------------------------------------
import anwp.func.datatype

class IndustryData(anwp.func.datatype.DataType):
    """A Industry Data object represents one type of Industry in detail"""
    def __init__(self, args):
        # Attributes
        anwp.func.datatype.DataType.__init__(self, args)
        self.cities = int() # number of cities required to run industry
        self.output = float() # output of industry
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'cities', 'output')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_industrydata.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        