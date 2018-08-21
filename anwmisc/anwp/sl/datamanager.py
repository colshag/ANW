# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# datamanager.py
# Contains the basic Category Classes and the DataManager.
# ---------------------------------------------------------------------------
import copy
from sim import SimObject

class Category:
    """ base class for all Category classes that describe
    simulation objects in the game.
    """
    def __init__(self, name):
        self.name = name

class SimCategory(Category):
    """I am a category class for simulation objects. Each sim category
    has data that allows it to create a different type of actual
    simObject."""
    def __init__(self, name, mobile, life, collide, threshold, source, image):
        Category.__init__(self, name)
        self.mobile = mobile
        self.life = life
        self.collide = collide
        self.threshold = threshold
        self.source = source + ".py"
        self.image = image
        
    def create(self):
        """Create a SimObject using my data as a template.
        """
        newSim = SimObject(self)
        return newSim


class DataManager:
    """Repository of category objects that define the types
    of simulation objects in the game.
    """
    def __init__(self):
        self.categories = {}    # lists of category objects
        self.initCategory("sims", initialSimCategories, SimCategory)        
        
    def initCategory(self, label, rawData, categoryClass):
        newCatList = []
        self.categories[label] = newCatList
        for data in rawData:
            cdata = copy.copy(data)
            newCatObj = apply( categoryClass, cdata)
            newCatList.append( newCatObj )

    def findCategory(self, name, categoryName):
        category = self.categories.get(categoryName, None)
        if not category:
            return None
        for cat in category:
            if cat.name == name:
                return cat

    def createInstance(self, name, categoryName, *args):
        category = self.findCategory(name, categoryName)
        if category:
            return apply(category.create, args)

initialSimCategories = [
     # name              mobile life collide threshold source        image
     ("mobile square",     1,     0,    1,     5,      "sourceQuad",   None),
     ("mobile rectangle",  1,     0,    1,     0,      "sourceSkinny", None),
     ("static square",     0,     0,    0,     0,      "sourceQuad",   None) ]
