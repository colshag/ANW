# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# city.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a city
# ---------------------------------------------------------------------------
import anwp.func.root

class City(anwp.func.root.Root):
    """A City Represents one City Object in ANW"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given City Name
        self.resourceFocus = str() # City Resource Focus (AL, CR, IA, EC)
        self.state = int() # 1=Running, etc..
        self.defaultAttributes = ('id', 'name', 'resourceFocus', 'state')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_city.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        