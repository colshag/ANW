# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testall.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This will test all programs
# ---------------------------------------------------------------------------

def TestAll():
    # Test all unit tests
    testFUNC = ['funcs', 'names', 'root', 'storedata', 'datatype']
 
    # func package
    for filename in testFUNC:
        filename = '%s.py' % filename
        execfile(filename)

if __name__ == "__main__":
    TestAll()