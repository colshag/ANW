# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# root.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents the root ANW class, common functions are stored 
# ---------------------------------------------------------------------------
import types

import funcs

class Root(object):
    """A ANW object contains generic ANW Methods."""
    def __init__(self, args):
        # The init is only used for testing and does not need to be called by child classes
        self.id = str()
        self.myInteger = int() # represent an integer
        self.myString = str() # represent a string
        self.myList = list()
        self.myFloat = float()
        self.defaultAttributes = ['id', 'myInteger', 'myString', 'myList']
        self.setAttributes(args)
        self.myDict = {} # represent a dictionary

    def clearAttribute(self, attr):
        """Clear an attribute if its a float"""
        myAttr = getattr(self, attr)
        if type(myAttr) == types.FloatType:
            if myAttr < 1.0 and myAttr > 0.0:
                setattr(self, attr, 0.0)

    def setAttributes(self, args):
        """Update Attributes, args is a dictionary"""
        for atr in self.defaultAttributes:
            if args.has_key(atr):
                # convert atr to proper type
                objAttr = getattr(self, atr)
                myType = type(args[atr])
                if type(objAttr) == types.IntType and myType <> types.IntType:
                    args[atr] = int(args[atr])
                elif type(objAttr) == types.StringType and myType <> types.StringType:
                    args[atr] = str(args[atr])
                elif type(objAttr) == types.ListType and myType <> types.ListType:
                    args[atr] = eval(args[atr])
                elif type(objAttr) == types.DictType and myType <> types.DictType:
                    args[atr] = eval(args[atr])
                elif type(objAttr) == types.FloatType and myType <> types.FloatType:
                    args[atr] = float(args[atr])
                setattr(self, atr, args[atr])
    
    def getMyInfoAsDict(self):
        """Return detailed information of this object in dictionary form"""
        dict = self.getSelectedAttr(list(self.defaultAttributes))
        return dict
    
    def getMyDictInfo(self, myChildDictName, childGetFunction='getMyInfoAsDict'):
        """Return a dict where key=myDict key, value= myDict object converted
        into a dict value
        getMyInfoAsDict is the normal function to return Dict of data, special
        child functions can return Dict data in a formatted way if required"""
        d = {}
        myDict = getattr(self, myChildDictName)
        for id, obj in myDict.iteritems():
            childObjGetFunction = getattr(obj, childGetFunction)
            d[id] = childObjGetFunction()
        return d
                
    def getAttributes(self, convertToString = False):
        """Take a list of args as keys return a list of values"""
        d = self.__dict__
        list = []
        
        # loop through list given return values in proper format
        for item in self.defaultAttributes:
            if d.has_key(item):
                if convertToString:
                    list.append(str(d[item]))
                else:
                    list.append(d[item])
        return list
    
    def getSelectedAttr(self, listAttrNames):
        """Take a list of Attr names and return a dict of those attributes values with names as keys"""
        d = {}
        for item in listAttrNames:
            if self.__dict__.has_key(item):
                d[item] = self.__dict__[item]
        return d
    
    def getNextID(self, d):
        """Take the dict given and find the next available ID"""
        try:
            listOrdered = d.keys()
            listOrdered = funcs.sortStringList(listOrdered)
            lastID = int(listOrdered[-1])
            nextID = str(lastID + 1)
            for i in range(1,int(nextID)):
                if str(i) not in listOrdered:
                    return str(i)
            return nextID
        except:
            return '1'
    
    def setMyDictInfo(self, myDict):
        """Take a dictionary where key = attribute name, value = value, if attribute is a dict itself
        then call setMyDictInfo on each object in that Dict"""
        for key, value in myDict.iteritems():
            myObj = getattr(self, key)
            if type(myObj) == types.DictType:
                # this is a dict of objects
                for key2, value2 in myObj.iteritems():
                    myChildObj = myObj[key2]
                    try:
                        myChildDict = myDict[key][key2]
                        myChildObj.setMyDictInfo(myChildDict)
                    except:
                        pass
                if type(value) == types.DictType and len(myObj.keys()) == 0:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_root.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()