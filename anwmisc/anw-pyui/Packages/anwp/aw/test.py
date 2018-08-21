# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testall.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This will test all programs
# ---------------------------------------------------------------------------

def TestAll():
    # Test all unit tests for ANW
    testAW = ['system','galaxy', 'empire', 'tech', 'city', 
              'industrydata', 'industry', 'order', 'mail', 'traderoute', 
              'marketstat', 'diplomacy']
    
    # aw package
    for filename in testAW:
        filename = '%s.py' % filename
        execfile(filename)

if __name__ == "__main__":
    TestAll()