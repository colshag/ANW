# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testall.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This will test all programs
# ---------------------------------------------------------------------------

def TestAll():
    # Test all unit tests
    testWAR = ['quad', 'ship', 'component', 'componentdata', 
               'weapon', 'weapondata', 'shiphulldata', 'shipdesign', 'captain',
               'shipsimulator', 'empire', 'shipbattle']
    
    # war package
    for filename in testWAR:
        filename = '%s.py' % filename
        execfile(filename)

if __name__ == "__main__":
    TestAll()