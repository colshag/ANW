# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# storedata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This stores and retrieves data from files using cPickle
# ---------------------------------------------------------------------------
import cPickle
import sys
    
def loadFromFile(filenamePath):
    """return object from filename"""
    try:
        FILE = open(filenamePath, 'r')
        obj = cPickle.load(FILE)
        FILE.close()
    except:
        print sys.exc_info()
    else:
        return obj

def loadFromString(stringOfObject):
    """return object from pickled string"""
    try:
        obj = cPickle.loads(stringOfObject)
    except:
        print 'unable to load object from string'
        return 0
    else:
        return obj

def saveToFile(obj, filenamePath):
    """Save object to filename"""
    try:
        FILE = open(filenamePath, 'wb')
        cPickle.dump(obj, FILE)
        FILE.close()
        return 1
    except:
        return 'Unable to Save File:%s' % filenamePath
    
def saveToString(obj):
    """Save Object into string and return"""
    try:
        stringOfObject = cPickle.dumps(obj)
        return stringOfObject
    except:
        print 'unable to save object to string'
        return 0
    
def printListToFile(list, filenamePath):
    """Print list to file"""
    try:
        FILE = open(filenamePath, 'w')
        for item in list:
            FILE.write(str(item))
        FILE.close()
        return 1
    except:
        return 'Unable to print File:%s' % filenamePath

  
