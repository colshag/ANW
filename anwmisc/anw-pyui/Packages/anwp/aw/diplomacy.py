# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# diplomacy.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a diplomatic state between two empires
# ---------------------------------------------------------------------------
import anwp.func.root

class Diplomacy(anwp.func.root.Root):
    """A Diplomacy Represents a Diplomatic State between two Empires"""
    def __init__(self, args):
        # Attributes
        self.empireID = str() # represents the other empire id
        self.diplomacyID = int() # Given Diplomacy id
        self.myIntent = str() # 'none', 'increase', 'decrease'
        self.empireIntent = str() # 'none', 'increase', 'decrease'
        self.defaultAttributes = ('empireID', 'diplomacyID', 'myIntent', 'empireIntent')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_diplomacy.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        