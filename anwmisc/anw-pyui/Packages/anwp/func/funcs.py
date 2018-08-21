# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# funcs.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# A Hodgepodge of useful functions
# ---------------------------------------------------------------------------
import types
import math
import random
import os
import fnmatch
import zlib
import base64

import globals
import anwp.sl

def compressString(myString):
    """Compress String for transfer over XML-RPC"""
    sz = zlib.compress(myString)
    s64 = base64.encodestring(sz)
    return s64

def decompressString(myString):
    """Decompress String after transfer"""
    s64 = base64.decodestring(myString)
    sz = zlib.decompress(s64)
    return sz

def all_files(root, patterns='*', single_level=False, yield_folders=False):
    # Expand patterns from semicolon-separated string to list
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break
        
def sortDictValues(d):
    """Return a list of values based on sorted keys from given dict"""
    keys = d.keys()
    try:
        if type(keys[0]) == types.StringType:
            keys = sortStringList(keys)
        else:
            keys.sort()
        if keys == -1:
            keys = d.keys()
            keys.sort()
    except:
        keys.sort()
    return [d[key] for key in keys]

def returnDictFromString(s, numChars):
    """Return a dictionary based on a string that is chopped into sections
    that based on a certain length"""
    x = 1
    d = {}
    if len(s) < numChars:
        d[1] = s
    else:
        while len(s) > (x * numChars):
            d[x] = s[(x-1)*numChars:x*numChars]
            x += 1
        d[x] = s[(x-1)*numChars:x*numChars]
    
    return d

def sortStringList(list):
    """Sort a list of strings properly when the strings are numbers in str form"""
    try:
        i = 0
        for item in list:
            if type(item) == types.IntType:
                return list
            try:
                item = int(item)
            except ValueError:
                # revert list back to string
                for item in list:
                    item = str(item)
                list.sort(key=str.lower)
                return list
            list[i] = item
            i += 1
            
        list.sort()
        i = 0
        
        for item in list:
            item = str(item)
            list[i] = item
            i += 1
        return list
    except:
        # on error return unsorted list
        return -1

def getAngleOffset(angle1, angle2):
    """get the nearest angle offset (either left or right on unit circle) between angles"""
    # get rid of negative angles
    angle1 = angle1 % 360
    angle2 = angle2 % 360
    if angle1+(360-angle2) < 180:
        return (angle1 - angle2) % 360
    elif angle2+(360-angle1) < 180:
        return (angle2 - angle1) % 360
    else:
        return abs(angle2 - angle1)

def getDamageColor(current, max):
    """return a color depending on the values of current and max"""
    if current == max:
        return globals.colors['white']
    elif current < max/2.0:
        return globals.colors['red']
    else:
        return globals.colors['yellow']

def getHitPosition(x1, y1, x2, y2, rotation):
    """Determine the quadrant position of a direct hit between shooter(x1,y1)
    and target (x2,y2) considering target's rotation"""
    angle = getRelativeAngle(x2,y2,x1,y1)
    angle = (angle - rotation) % 360
    if angle > 45 and angle <= 135:
        return 'port'
    elif angle > 135 and angle < 225:
        return 'aft'
    elif angle >= 225 and angle <= 315:
        return 'star'
    else:
        return 'fore'

def getMapQuadrant(fromX, fromY, toX, toY):
    """Using the from and to System Coordinates, determine and return ship 
    Battle Map Quadrant:  7,8,9
                          4,5,6
                          1,2,3"""
    if fromX == toX:
        if fromY < toY:
            return 2
        elif fromY == toY:
            return 5
        elif fromY > toY:
            return 8
    elif fromX < toX:
        if fromY < toY:
            return 1
        elif fromY == toY:
            return 4
        elif fromY > toY:
            return 7
    elif fromX > toX:
        if fromY < toY:
            return 3
        elif fromY == toY:
            return 6
        elif fromY > toY:
            return 9

def getNiceNumber(num):
    """Return 1st, 2nd, 3rd, 4th, etc given the number"""
    myList = ['st','nd','rd']
    if num <= len(myList):
        return '%d%s' % (num, myList[num-1])
    else:
        return '%dth' % num

def getRandomD100Rolls(numberOfRolls):
    """Return a List of D100Rolls"""
    rolls = []
    for i in range(numberOfRolls):
        rolls.append(random.randint(1, 100))
    return rolls

def getRelativeAngle(x1, y1, x2, y2):
    """Return the Relative Angle from Point A's perspective between point 
    A and point B.  Return in degrees"""
    dx = x2-x1
    dy = y2-y1
    angle = 0.0

    # calculate angle
    if dx == 0.0:
        if dy == 0.0:
            angle = 0.0
        elif dy > 0.0:
            angle = math.pi / 2.0
        else:
            angle = math.pi * 3.0 / 2.0  
    elif dy == 0.0:
        if  dx > 0.0:
            angle = 0.0
        else:
            angle = math.pi
    else:
        ratio = float(dy)/float(dx)
        if  dx < 0.0:
            angle = math.atan(ratio) + math.pi
        elif dy < 0.0:
            angle = math.atan(ratio) + (2 * math.pi)
        else:
            angle = math.atan(ratio)
        
    # convert to degrees
    angle = 180.0*angle/math.pi
    
    if angle < 0:
        angle += 360.0
    return angle

def getXYfromAngle(x, y, distance, angle):
    """Return x, y from original x, y, their distance apart, and relative angle
    assume angle is in degrees"""
    angle = math.pi*angle/180.0
    offsetY = math.sin(angle) * distance
    offsetX = math.cos(angle) * distance
    return (x + offsetX, y + offsetY)

def findOffset(x, y, direction, distance):
        """given an x, y and direction, return offset x,y using distance from direction
        """
        radians = anwp.sl.utils.toRadians(direction)
        dx = math.cos(radians) * distance
        dy = math.sin(radians) * distance
        return (x + dx, y + dy)

def getOffsetPoint(x1, y1, x2, y2, offset):
    """Get an offset point value based on the x and y values of 2 points"""
    # find middle point
    x = x1 - ((x1-x2)/2)
    y = y1 - ((y1-y2)/2)
    
    # offset point depending on placement
    angle = getRelativeAngle(x1,y1,x2,y2)
    if angle == 0.0:
        y -= offset
    elif angle <= 45.0:
        x += offset
        y -= offset
    elif angle <= 90.0:
        x += offset
    elif angle <= 135.0:
        x += offset
        y += offset
    elif angle <= 180.0:
        y += offset
    elif angle <= 225.0:
        x -= offset
        y += offset
    elif angle <= 270.0:
        x -= offset
    elif angle <= 315.0:
        x -= offset
        y -= offset
    else:
        y -= offset
    
    return (x,y)

def getTargetRange(xMe, yMe, xTar, yTar):
    """Get Actual Range between two points"""
    actRange = math.sqrt((xMe-xTar)**2 + (yMe-yTar)**2)
    return actRange

def getTargetRangeSquared(xMe, yMe, xTar, yTar):
    """Get Actual Range between two points Squared, this saves on doing square roots"""
    actRange = (xMe-xTar)**2 + (yMe-yTar)**2
    return actRange

def getTargetRotate(xMe, yMe, xTar, yTar, myFacing):
    """Rotate towards target"""
    # get relative angle between ship and target
    angle = getRelativeAngle(xMe, yMe, xTar, yTar)
    targetAngle = angle - myFacing
    targetAngle = targetAngle % 360
    if targetAngle == 0 or targetAngle == 360:
        return 0
    elif targetAngle > 180:
        return -1 # turn right
    elif targetAngle <= 180 and targetAngle > 0:
        return 1 # turn left
    elif targetAngle < 0:
        return -1 # turn right
    else:
        return 0 # do nothing          
            
def sortDictByChildObjValue(parentDict, valueToSort, reverse, mustEqualDict):
    """Return sorted list of child Objects based on the sorting of a parent dictionary"""
    d = {}
    for parentKey, childObj in parentDict.iteritems():
        # create new temp dict to sort
        if len(mustEqualDict.keys()) == 0:
            try:
                # child value is an attribute
                d[parentKey] = getattr(childObj, valueToSort)
            except AttributeError:
                # child value is a dictionary key
                d[parentKey] = childObj[valueToSort]
                
        else:
            # only allow through items that meet criteria of mustEqualDict
            i = 1
            for key, value in mustEqualDict.iteritems():
                if getattr(childObj, key) <> value:
                    i = 0
            if i == 1:
                d[parentKey] = getattr(childObj, valueToSort)
        
    # sort temp dict by childValue
    sortedKeys = sortDictByValue(d, reverse)
    newList = []
    
    # build new sorted list of Dictionaries
    for key in sortedKeys:
        newList.append(parentDict[key])
    return newList

def sortDictByValue(d, rev=False):
    """Returns the list of keys of dictionary d sorted by their values"""
    items=d.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort(reverse=rev)
    return [ backitems[i][1] for i in range(0,len(backitems))]

def targetInRangeArcOrig(myFacing, xMe, yMe, xTar, yTar, weapRange, weapArc):
    """Return range if target in range and arc of Me, else return 0"""
    range = getTargetRange(xMe, yMe, xTar, yTar)
    if range <= weapRange:
        # check Arc
        relativeFacing = getRelativeAngle(xMe, yMe, xTar, yTar)
        facingDiff = getAngleOffset(myFacing, relativeFacing)
        if facingDiff <= weapArc/2:
            return range
    else:
        return 0

def targetInRangeArc(myFacing, xMe, yMe, xTar, yTar, weapRange, weapArc):
    """Return range if target in range and arc of Me, else return 0.

    This method is an optimized version of targetInRangeArcOrig. All that
    was done was to move the contents of any method it called into the local method
    body in order to avoid incurring the cost of method invocation which is high
    in python. Now the method executes in ~1/2 the time.
    
    This is one of the most called methods during a simulation, on the order of millions
    of invocations for a regular sized battle."""
    range = math.sqrt((xMe-xTar)**2 + (yMe-yTar)**2)
    if range <= weapRange:
        # check Arc
        # relativeFacing = getRelativeAngle(xMe, yMe, xTar, yTar)
        relativeFacing = 0
        
        """Return the Relative Angle from Point A's perspective between point 
        A and point B.  Return in degrees"""
        dx = xTar-xMe
        dy = yTar-yMe
        angle = 0.0

        # calculate angle
        if dx == 0.0:
            if dy == 0.0:
                angle = 0.0
            elif dy > 0.0:
                angle = math.pi / 2.0
            else:
                angle = math.pi * 3.0 / 2.0  
        elif dy == 0.0:
            if  dx > 0.0:
                angle = 0.0
            else:
                angle = math.pi
        else:
            ratio = float(dy)/float(dx)
            if  dx < 0.0:
                angle = math.atan(ratio) + math.pi
            elif dy < 0.0:
                angle = math.atan(ratio) + (2 * math.pi)
            else:
                angle = math.atan(ratio)
            
        # convert to degrees
        angle = angle * 180.0 / math.pi
        
        if angle < 0:
            angle += 360.0

        relativeFacing=angle

        """get the nearest angle offset (either left or right on unit circle) between angles"""
        # get rid of negative angles
        facingDiff = 0
        angle1 = myFacing % 360
        angle2 = relativeFacing % 360
        if angle1+(360-angle2) < 180:
            facingDiff = (angle1 - angle2) % 360
        elif angle2+(360-angle1) < 180:
            facingDiff = (angle2 - angle1) % 360
        else:
            facingDiff = abs(angle2 - angle1)

        if facingDiff <= weapArc/2:
            return range
        else:
            return 0
    else:
        return 0

def isMac():
    """Returns true if this is MacOSX"""
    import sys
    return sys.platform == 'darwin'

def isMacPPC():
    """Returns true if this a PowerPC Processor MacOSX"""
    import sys
    return isMac() and sys.byteorder == 'big'

def isMacIntel():
    """Returns true if this is an Intel Processor MacOSX"""
    import sys
    return isMac() and sys.byteorder == 'little'

def perfTest():
    for i in xrange(100000):
        targetInRangeArc(0,1,2,3,4,10,20)
        targetInRangeArcOrig(0,1,2,3,4,10,20)
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_func.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    #import profile
    #profile.run('perfTest()')
    main()

  
