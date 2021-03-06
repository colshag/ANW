# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# regimentdata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for marine regiments
# ---------------------------------------------------------------------------
import anwp.func.datatype

class RegimentData(anwp.func.datatype.DataType):
    """A Regiment Data object represents one type of Regiment in detail"""
    def __init__(self, args):
        # Attributes
        anwp.func.datatype.DataType.__init__(self, args)
        self.power = float() # specific regiment power rating
        self.L = float() # regiment percentile vs militia
        self.I = float() # regiment percentile vs infantry marines
        self.M = float() # regiment percentile vs machanized marines
        self.A = float() # regiment percentile vs artillery marines
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'power','L','I','M','A')
        self.setAttributes(args)
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_regimentdata.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        