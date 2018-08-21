# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_funcs.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The function of funcs is to provide general functions for many uses
# ---------------------------------------------------------------------------
from anw.func import funcs
from anw.func.misc import near

class TestFuncs(object):
    
    def testGetPurchaseNumFromFunds(self):
        """How many times can item be purchased given available funds and item cost
        both are in lists [CR,AL,EC,IA]"""
        result = funcs.getPurchaseNumFromFunds(funds=(100,100,100,100),
                                               cost=(10,10,10,10))
        assert result == 10
        result = funcs.getPurchaseNumFromFunds(funds=(100,100,100,10),
                                               cost=(10,10,10,10))
        assert result == 1
        result = funcs.getPurchaseNumFromFunds(funds=(100,100,100,5),
                                               cost=(10,10,10,10))
        assert result == 0
        result = funcs.getPurchaseNumFromFunds(funds=(-100,10,10,10),
                                               cost=(10,10,10,10))
        assert result == 0
    
    def testGetRelativeAngle(self):
        """Return the Relative Angle from Point A's perspective between point 
        A and point B.  Return in degrees"""
        testGroup = {0.0:(18.0,36.0,18.0,42.0),
                     45.0:(18.0,36.0,24.0,42.0),
                     90.0:(18.0,36.0,24.0,36.0),
                     135.0:(18.0,36.0,24.0,30.0),
                     180.0:(18.0,36.0,18.0,30.0),
                     225.0:(18.0,36.0,12.0,30.0),
                     270.0:(18.0,36.0,12.0,36.0),
                     315.0:(18.0,36.0,12.0,42.0),
                     315.0:(0,0,-1.0,1.0),
                     63.43494882292201:(0,0,2.0,1.0),
                     26.565051177077997:(0,0,1.0,2.0),
                     116.56505117707799:(0,0,2.0,-1.0),
                     153.434948822922003:(0,0,1.0,-2.0),
                     206.565051177078:(0,0,-1.0,-2.0),
                     243.43494882292202:(0,0,-2.0,-1.0),
                     333.43494882292202:(0,0,-1.0,2.0),
                     296.56505117707798:(0,0,-2.0,1.0),
                     }
        
        for assumedResult, (x1,y1,x2,y2) in testGroup.iteritems():
            result = funcs.getRelativeAngle(x1,y1,x2,y2)
            assert near(result, assumedResult)
    
    def testFindOffset(self):
        """Given an x, y and direction, return offset x,y using distance from direction"""
        testGroup = {(5.0,3.0615158845559431e-16):(0.0,0.0,90.0,5.0),
                     (-5.0,-9.1845476536678294e-16):(0.0,0.0,270.0,5.0),
                     (0.0,5.0):(0.0,0.0,0.0,5.0),
                     (6.1230317691118863e-16,-5.0):(0.0,0.0,180.0,5.0),
                     ( 0.70709999999999995, 0.70709999999999995):(0.0,0.0,45.0,1.0),
                 }
        
        for assumedResult, (x,y,direction,distance) in testGroup.iteritems():
            result = funcs.findOffset(x,y,direction,distance)
            assert near(assumedResult[0], result[0])
            assert near(assumedResult[1], result[1])
    
    def testGetTargetRotate(self):
        """Rotate towards target"""
        testGroup = {0:(18.0,36.0,18.0,42.0, 0.0),
                     1:(18.0,36.0,24.0,42.0, 0.0),
                     1:(18.0,36.0,24.0,36.0, 45.0),
                     -1:(18.0,36.0,24.0,30.0, 155.0),
                     1:(18.0,36.0,18.0,30.0, 0.0),
                     -1:(18.0,36.0,12.0,30.0, 0.0),
                     -1:(18.0,36.0,12.0,36.0, 0.0),
                     -1:(18.0,36.0,12.0,42.0, 0.0),
                     -1:(0,0,-10,-10,0.0),
                     1:(-10,0,0,0,0.0)
                     }
        
        for assumedResult, (x1,y1,x2,y2,myFacing) in testGroup.iteritems():
            assert assumedResult == funcs.getTargetRotate(x1,y1,x2,y2,myFacing)
    
    def testDoWeCollide(self):
        """Do two things collide given x, y, radius of both"""
        testGroup = {1:(52,52,2,50,50,3),
                     0:(56,52,2,50,50,3)
                    }
        for assumedResult, (x1, y1, r1, x2, y2, r2) in testGroup.iteritems():
            assert assumedResult == funcs.doWeCollide(x1, y1, r1, x2, y2, r2)
    
    def testGetTargetRange(self):
        """Get Actual Range between two points"""
        testGroup = {0:(0,0,0,0),
                     1.4142135623730951:(0,0,1,1),
                     1.4142135623730951:(0,0,-1,1),
                     2.8284271247461903:(0,0,-2,2),
                     }
        for assumedResult, (x1, y1, x2, y2) in testGroup.iteritems():
            assert assumedResult == funcs.getTargetRange(x1, y1, x2, y2)
    
    def testGetDamageColor(self):
        """Return a color depending on the values of current and max"""
        from pandac.PandaModules import Vec4
        testGroup = {Vec4(0,1,0,1):(100,100),
                     Vec4(1,0,0,1):(20,100),
                     Vec4(0.922,0.910,0.047,1):(90,100)
                     }
        for assumedResult, (current, max) in testGroup.iteritems():
            assert assumedResult == funcs.getDamageColor(current, max)
    
    def getFutureColor(self):
        """Return a color based on if the new number is different then the old color"""
        from pandac.PandaModules import Vec4
        testGroup = {Vec4(1,1,1,1):(10,10),
                     Vec4(1,0,0,1):(2,10),
                     Vec4(0,1,0,1):(10,1)
                     }
        for assumedResult, (newNum, oldNum) in testGroup.iteritems():
            assert assumedResult == funcs.getFutureColor(newNum, oldNum)
            
    def testGetHitPosition(self):
        """Determine the quadrant position of a direct hit between shooter(x1,y1)
        and target (x2,y2) considering target's rotation"""
        testGroup = {'port':(-1,0,   0,0,  0),
                     'star':(1,0,    0,0,  0),
                     'fore':(0,1,    0,0,  0),
                     'aft': (0,-1,   0,0,  0),
                     'port':(-10,-5, 0,0,  0),
                     'aft':(-5,-10,  0,0,  0),
                     'star':(-1,0,   0,0,  180),
                     'port':(1,0,    0,0,  180),
                     'aft':(0,1,    0,0,  180),
                     'fore': (0,-1,   0,0,  180),
                     'star':(-10,-5, 0,0,  180),
                     'fore':(-5,-10,  0,0,  180),
                     }
        for assumedResult, (x1, y1, x2, y2, rotation) in testGroup.iteritems():
            assert assumedResult == funcs.getHitPosition(x1, y1, x2, y2, rotation)
    
    def testTargetInRangeArc(self):
        """Return range if target in range and arc of Me, else return 0.

        This method is an optimized version of targetInRangeArcOrig. All that
        was done was to move the contents of any method it called into the local method
        body in order to avoid incurring the cost of method invocation which is high
        in python. Now the method executes in ~1/2 the time.
        
        This is one of the most called methods during a simulation, on the order of millions
        of invocations for a regular sized battle."""
        testGroup = {10:(90,  0,0,  10,0,  20,  10),
                     0:(90,  0,0,  10,0,  5,  10),
                     10:(0,  0,0,  0,10,  20,  10),
                     14.142135623730951:(40,  0,0,  10,10,  20,  10),
                     0:(40,  0,0,  10,10,  20,  2),
                     14.142135623730951:(220,  0,0,  -10,-10,  20,  10)
                     }
        for assumedResult, (myFacing, x1, y1, x2, y2, weapRange, weapArc) in testGroup.iteritems():
            assert assumedResult == funcs.targetInRangeArc(myFacing, x1, y1, x2, y2, weapRange, weapArc)
            
    def testSortDictByValue(self):
        """Returns the list of keys of dictionary d sorted by their values"""
        d = {1:2, 2:3, 3:1, 4:4, 5:6, 6:5}
        resultList = funcs.sortDictByValue(d)
        assert resultList == [3, 1, 2, 4, 6, 5]
        resultList = funcs.sortDictByValue(d, True)
        assert resultList == [5, 6, 4, 2, 1, 3]
        
                        