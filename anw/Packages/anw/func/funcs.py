# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
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

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from random import randrange

def getTrueOrFalse(value):
    """return a True or False based on value given"""
    if value in (1,'1','True','yes','Yes','Y'):
        return True
    else:
        return False

def getSystemName(systemDict):
    """Return System Name taking into account warp"""
    text = ''
    if 'availWGC' in systemDict.keys():
        availWGC = systemDict['availWGC']
        if availWGC != 0:
            text = '%s -> (%d/%d)' % (systemDict['name'], systemDict['usedWGC'], availWGC)
        else:
            text = systemDict['name']
    else:
        text = systemDict['name']
    return text

def setZeroToText(myText, value):
    """Add a zero if text is less then 10"""
    strValue = str(value)
    if len(strValue) == 1:
        strValue = '0' + strValue
    myText.setText(' %s' % strValue)
    setTextColor(myText, value)

def setTextColor(myText, value):
    """Make text Green if positive, red if negative"""
    if value < 0:
        myText.setTextColor(globals.colors['guired'])
    elif value > 0:
        myText.setTextColor(globals.colors['guigreen'])
    else:
        myText.setTextColor(globals.colors['guiblue1'])

def getTransportsRequired(regimentNum):
    """Return the number of transports required based on regiment number"""
    num = regimentNum/globals.marinesPerTransport
    if regimentNum % globals.marinesPerTransport > 0:
        num += 1
    return num

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

def getPurchaseNumFromFunds(funds, cost):
    """How many times can item be purchased given available funds and item cost
    both are in lists [CR,AL,EC,IA]"""
    if funds[0] <= 0:
        return 0
    max = 999
    for i in range(4):
        if cost[i] > 0:
            value = funds[i]/cost[i]
            if value < max:
                max = value
    return max

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
    """Return a color depending on the values of current and max"""
    if current == max:
        return globals.colors['guigreen']
    elif current < max/2.0:
        return globals.colors['guired']
    else:
        return globals.colors['guiyellow']

def getFutureColor(newNum, oldNum):
    """Return a color based on if the new number is different then the old color"""
    if newNum == oldNum:
        return globals.colors['guiwhite']
    elif newNum < oldNum:
        return globals.colors['guired']
    elif newNum > oldNum:
        return globals.colors['guigreen']

def getHitPosition(x1, y1, x2, y2, rotation):
    """Determine the quadrant position of a direct hit between shooter(x1,y1)
    and target (x2,y2) considering target's rotation"""
    angle = getRelativeAngle(x2,y2,x1,y1)
    angle = (angle - rotation) % 360
    if angle > 45 and angle <= 135:
        return 'star'
    elif angle > 135 and angle < 225:
        return 'aft'
    elif angle >= 225 and angle <= 315:
        return 'port'
    else:
        return 'fore'

def getMapQuadrant(system,ship,fromX, fromY, toX, toY):
    """Use ship loyalties to system owner to decide placement
    defenders on quadrant 9,6,3, attackers on quadrant 7,4,1
    
    Battle Map Quadrant:  7,8,9
                          4,5,6
                          1,2,3"""
    if system.myEmpireID == ship.empireID:
        defender = 1
    elif globals.diplomacy[system.myEmpire.diplomacy[ship.empireID].diplomacyID]['engage'] == 0:
        defender = 1
    else:
        defender = 0
        
    if defender == 1:
        if fromY < toY:
            return 3
        elif fromY == toY:
            return 6
        elif fromY > toY:
            return 9
    else:
        if fromY < toY:
            return 1
        elif fromY == toY:
            return 4
        elif fromY > toY:
            return 7

def getSimQuadrant(ship):
    """Simulations don't have the system objects available to them and don't need them"""
    if ship.empireID == '1':
        return 9
    else:
        return 1
        
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

    if dx == 0.0:
        if dy == 0.0:
            angle = 0.0
        elif dy > 0.0:
            angle = 0.0
        else:
            angle = 180.0
    elif dy == 0.0:
        if  dx > 0.0:
            angle = 90.0
        else:
            angle = 270.0
    else:
        angle = math.atan2(abs(dy),abs(dx))
        angle = math.degrees(angle)
        if dx >= 0 and dy >= 0:#quad 1
            angle = 90.0-angle
        elif dx >= 0 and dy < 0:#quad 2
            angle = 90.0+angle
        elif dx < 0 and dy < 0:#quad 3
            angle = 270.0-angle
        elif dx < 0 and dy >= 0:#quad 4
            angle = 270.0+angle

    return angle%360

def getXYfromAngle(x, y, distance, angle):
    """Return x, y from original x, y, their distance apart, and relative angle
    assume angle is in degrees"""
    angle = math.pi*angle/180.0
    offsetY = math.sin(angle) * distance
    offsetX = math.cos(angle) * distance
    return (x + offsetX, y + offsetY)

def findOffset(x, y, direction, distance):
    """Given an x, y and direction, return offset x,y using distance from direction
    """
    radians = math.radians(direction)
    dx = math.sin(radians) * distance
    dy = math.cos(radians) * distance
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

def doWeCollide(xMe, yMe, radiusMe, xTar, yTar, radiusTar):
    """Return 0 if no collision, return 1 if collision"""
    dist = radiusMe + radiusTar
    if abs(xMe-xTar) <= dist:
        if abs(yMe-yTar) <= dist:
            return 1
    return 0

def getShipNum(myShipDesign, battleValue=300.0):
    """Return the number of ships to build from ship design based on battle value"""
    num = battleValue/myShipDesign.getMyBattleValue()
    num = int(num)
    return num

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
    angle = getRelativeAngle(xMe, yMe, xTar, yTar)
    targetAngle = (angle - myFacing) % 360
    if targetAngle == 0 or targetAngle == 360:
        return 0
    elif targetAngle > 180:
        return -1 # turn left
    elif targetAngle <= 180 and targetAngle > 0:
        return 1 # turn right
    return 0
            
def sortDictByChildObjValue(parentDict, valueToSort, reverse=True , mustEqualDict={}):
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
                if getattr(childObj, key) != value:
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

def targetInRangeArc(myFacing, x1, y1, x2, y2, weapRange, weapArc):
    """Return range if target in range and arc of Me, else return 0.

    This method is an optimized version of targetInRangeArcOrig. All that
    was done was to move the contents of any method it called into the local method
    body in order to avoid incurring the cost of method invocation which is high
    in python. Now the method executes in ~1/2 the time.
    
    This is one of the most called methods during a simulation, on the order of millions
    of invocations for a regular sized battle."""
    range = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    if range <= weapRange:
        # check Arc
        # relativeFacing = getRelativeAngle(x1,y1,x2,y2)
        relativeFacing = 0
        
        """Return the Relative Angle from Point A's perspective between point 
        A and point B.  Return in degrees"""
        dx = x2-x1
        dy = y2-y1
        angle = 0.0
    
        if dx == 0.0:
            if dy == 0.0:
                angle = 0.0
            elif dy > 0.0:
                angle = 0.0
            else:
                angle = 180.0
        elif dy == 0.0:
            if  dx > 0.0:
                angle = 90.0
            else:
                angle = 270.0
        else:
            angle = math.atan2(abs(dy),abs(dx))
            angle = math.degrees(angle)
            if dx >= 0 and dy >= 0:#quad 1
                angle = 90.0-angle
            elif dx >= 0 and dy < 0:#quad 2
                angle = 90.0+angle
            elif dx < 0 and dy < 0:#quad 3
                angle = 270.0-angle
            elif dx < 0 and dy >= 0:#quad 4
                angle = 270.0+angle

        relativeFacing=angle%360

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

def sendMail(to, subject, text):
    """Send mail to users using gmail server"""
    try:
        emailServers = ["tybjeajjsssdddec","cvecsiynwijoqwcc","bztuerbojdxobebe"]
        random_index = randrange(len(emailServers))
        serverName = "cosmicaserver%d" % random_index
        fromaddr = "%s@gmail.com" % serverName
        toaddr = to
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject

        body = text
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(serverName, emailServers[random_index])
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)            
    except:
        print 'Error: Could not send email to:%s' % to

def getTodaysDateAsString():
    import datetime
    return datetime.date.today().strftime("%A %d. %B %Y")
    
    
    
    
