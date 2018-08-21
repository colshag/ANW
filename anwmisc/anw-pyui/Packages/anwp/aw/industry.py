# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# industry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an industry object
# ---------------------------------------------------------------------------
import anwp.func.root

class Industry(anwp.func.root.Root):
    """A Industry Represents one Industry Object in ANW"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.industrytype = str() # id of industrydata of galaxy
        self.state = int() # 1=Running, etc..
        self.defaultAttributes = ('id', 'industrytype', 'state')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_industry.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        