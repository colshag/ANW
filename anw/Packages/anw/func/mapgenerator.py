# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# mapgenerator.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The Map Generator generates a map file randomly based on initial parameters
# ---------------------------------------------------------------------------
import random
from anw.func import funcs

class MapGenerator(object):
    """The Map Generator Generates the parameters needed to create a Galactic map:
    numEmpires = 5

genSystemsLegend = {'a': ('0', 10),
                    'b': ('0', 15),
                    'A': ('0', 20),
                    'B': ('0', 30),
                    'X': ('0', 50),
                    'c': ('1', 10),
                    'd': ('1', 15),
                    'C': ('1', 20),
                    'D': ('1', 40),
                    'e': ('2', 10),
                    'f': ('2', 15),
                    'E': ('2', 20),
                    'F': ('2', 40),
                    'g': ('3', 10),
                    'h': ('3', 15),
                    'G': ('3', 20),
                    'H': ('3', 40),
                    'i': ('4', 10),
                    'j': ('4', 15),
                    'I': ('4', 20),
                    'J': ('4', 40),
                    '.': (None, None)
                    }

genSystemsData =[
    'acCcaaBaaeEea',
    'adDda.A.afFfa',
    'aa.a.b.b.a.aa',
    'ABA.A.X.A.ABA',
    'aa.a.b.b.a.aa',
    'ajJja.A.ahHha',
    'aiIiaaBaagGga'
    ]

    """
    def __init__(self, width, height, empireNum, minDist, supportNum):
        self.width = width
        self.height = height
        self.empireNum = empireNum
        self.minDist = minDist
        self.supportNum = supportNum
        self.grid = {}
        self.homeworlds = []
        self.legend = {('0', 10):'a',
                        ('0', 15):'b',
                        ('0', 20):'A',
                        ('0', 30):'B',
                        ('0', 50):'X',
                        ('1', 10):'c',
                        ('1', 15):'d',
                        ('1', 20):'C',
                        ('1', 40):'D',
                        ('2', 10):'e',
                        ('2', 15):'f',
                        ('2', 20):'E',
                        ('2', 40):'F',
                        ('3', 10):'g',
                        ('3', 15):'h',
                        ('3', 20):'G',
                        ('3', 40):'H',
                        ('4', 10):'i',
                        ('4', 15):'j',
                        ('4', 20):'I',
                        ('4', 40):'J',
                        ('5', 10):'k',
                        ('5', 15):'l',
                        ('5', 20):'K',
                        ('5', 40):'L',
                        ('6', 10):'m',
                        ('6', 15):'n',
                        ('6', 20):'M',
                        ('6', 40):'N',
                        ('7', 10):'o',
                        ('7', 15):'p',
                        ('7', 20):'O',
                        ('7', 40):'P',
                        ('8', 10):'q',
                        ('8', 15):'r',
                        ('8', 20):'Q',
                        ('8', 40):'R',
                        (None, None):'.'
                    }
        self.spread = [(None, None),
                       (None, None),
                       (None, None),
                       (None, None),
                       ('0', 10),
                       ('0', 10),
                       ('0', 10),
                       ('0', 15),
                       ('0', 15),
                       ('0', 20),
                       ('0', 20),
                       ('0', 30),
                       ]
        self.cities = []
        for i in range(self.supportNum):
            self.cities.append(random.choice([10,15,15,20,20]))
        self.generateSystems()
    
    def generateSystems(self):
        """Create the systems needed for the map"""
        for x in range(0,self.width):
            for y in range(0,self.height):
                self.grid[(x,y)] = random.choice(self.spread)
        
        self.genHomeSystems()
        
    def genHomeSystems(self):
        self.homeworlds = []##[(self.width/2, self.height/2)]
        while 1:
            positions = self.grid.keys()
            random.shuffle(positions)
            myPosition = positions[0]
            if myPosition not in self.homeworlds:
                if self.amITooClose(myPosition):
                    self.homeworlds.append(myPosition)
            if len(self.homeworlds) == self.empireNum:
                self.addHomeworlds()
                return
    
    def amITooClose(self, myPosition):
        (x,y) = myPosition
        maxX = self.width-1
        maxY = self.height-1
        ##(xc,yc) = self.homeworlds[0]
        if (x,y) in [(0,0), (0,maxY), (maxX,0), (maxX,maxY)]:
            return 0
        ##range = funcs.getTargetRange(x,y,xc,yc)
        ##if range < self.minDist+1:
            ##return 0
        for (x2,y2) in self.homeworlds:
            range = funcs.getTargetRange(x,y,x2,y2)
            if range < self.minDist:
                return 0
        return 1
    
    def addHomeworlds(self):
        ##self.homeworlds.remove((self.width/2, self.height/2))
        count = 1
        for grid in self.homeworlds:
            empireID = '%d' % count
            self.grid[grid] = (empireID, 40)
            self.addSupportSystems(grid[0], grid[1], empireID)
            count += 1
     
    def addSupportSystems(self, homeX, homeY, empireID):
        mX = 0
        mY = 0
        cityNum = 0
        for x in range(-1,2):
            for y in range(-1,2):
                if cityNum > (self.supportNum-1):
                    return
                mX = x+homeX
                mY = y+homeY
                if self.isValidPosition(mX, mY, empireID):
                    self.grid[(mX,mY)] = (empireID, self.cities[cityNum])
                    cityNum += 1
    
    def isValidPosition(self, x, y, empireID):
        if x < 0 or x > (self.width-1) or y < 0 or y > (self.height-1):
            return 0
        position = self.grid[(x,y)]
        if position != (None,None):
            if position[0] != '0':
                return 0
        return 1
            
    def getSystemsData(self):
        return self.createSystemsDataFromGrid()
    
    def createSystemsDataFromGrid(self):
        myList = []
        for y in range(0,self.height):
            s = ''
            for x in range(0,self.width):
                s = s + self.legend[self.grid[(x,y)]]
            myList.append(s)
        return myList
    
if __name__ == "__main__":
    #mapgen = MapGenerator(width=16,height=10,empireNum=9,minDist=4, supportNum=4)
    #mapgen = MapGenerator(width=9,height=9,empireNum=5,minDist=4, supportNum=4)
    #mapgen = MapGenerator(width=10,height=9,empireNum=6,minDist=4, supportNum=4)
    #mapgen = MapGenerator(width=14,height=10,empireNum=8,minDist=4, supportNum=4)
    mapgen = MapGenerator(width=8,height=6,empireNum=3,minDist=4, supportNum=4)
    print mapgen.getSystemsData()
    
    