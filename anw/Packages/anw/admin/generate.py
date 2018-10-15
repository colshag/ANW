# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# generate.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The function of generate is to build up a galaxy object for admin purposes
# ---------------------------------------------------------------------------
import os
import string
import csv
import random

from anw.func import funcs, globals, names
from anw.aw import galaxy, empire, system, tech, industrydata, ai
from anw.war import regimentdata, componentdata, shiphulldata, weapondata

class GenerateGalaxy(object):
    """Generate a galaxy object"""
    def __init__(self):
        self.myGalaxy = None
        self.dataPath = ''
        self.generateSystems = None
        self.generateTech = None
        self.galaxyName = "ANW1"

    def genGalaxy(self, dataPath, starMapFile, playerList=[], doAI=0, galaxyName = "ANW1", serverPort=8000):
        """Generate a Galaxy Object given data path, and star Map data file"""
        self.galaxyName = galaxyName
        self.setDataPath(dataPath)
        self.genInitialGalaxy()
        self.setTemplateData('commonmap.data')
        self.setTemplateData(starMapFile)
        self.myGalaxy.setGalacticMarket()
        self.genDataTypes()
        self.genEmpires(playerList)
        self.genSystems()
        self.genDefaults()
        self.myGalaxy.endRound(doAITurn=doAI)
        self.genDesigns()
        self.genNeutralShips()
        self.myGalaxy.serverPort = serverPort
    
    def getGalaxy(self):
        """Return the galaxy object"""
        return self.myGalaxy
    
    def setGalaxy(self, myGalaxy):
        """Set the Galaxy"""
        self.myGalaxy = myGalaxy
    
    def setDataPath(self, path):
        """Set the Data Path to gather Galaxy Information"""
        self.dataPath = path
    
    def getDataFilesAsList(self):
        """Get the Data Files in Data Directory"""
        for root, dirs, files in os.walk(self.dataPath):
            return files
    
    def genInitialGalaxy(self):
        """Setup the Initial Galaxy"""
        d = {'name':self.galaxyName, 'version':globals.currentVersion, 'systemSize':globals.systemSize, 'currentRound':0}
        self.myGalaxy = galaxy.Galaxy(d)
    
    def setTemplateData(self, templateFileName):
        """Setup the Galaxy attributes from Template File, eg. starMap4A.map"""
        templateFilePath = os.path.normpath(self.dataPath + "/" + templateFileName)
        myDict = {"__builtins__":None,
                  "range" : range
                  }
        execfile(templateFilePath, myDict)
        self.myGalaxy.__dict__.update(myDict)
    
    def genEmpires(self, playerList=[]):
        if len(playerList) < self.myGalaxy.numEmpires:
            playerList = self.insertAIPlayers(playerList)
        if playerList[0] <> 'singleplayer':
            random.shuffle(playerList)
        self.genEmpire(0)
        for i in range(1,self.myGalaxy.numEmpires):
            self.genEmpire(i, playerList.pop(0))
    
    def insertAIPlayers(self, playerList):
        """add AI players if the number of human players is less then the number required from the map layout"""
        while len(playerList) < (self.myGalaxy.numEmpires - 1):
            playerList.append('ai')
        return playerList
        
    def genEmpire(self, id, player=''):
        """Create an Empire"""
        d = globals.empires[id]
        d['player'] = player
        d['delay'] = 0
        d['level'] = 1
        d['experience'] = 100.0
        myEmpire = empire.Empire(d)
        myEmpire.setMyGalaxy(self.myGalaxy)
        myEmpire.setInitialDiplomacy()
        myEmpire.CR = self.myGalaxy.startingCredits
        self.genTech(myEmpire.id)
        self.genAIPlayer(myEmpire)
        if player == 'ai':
            myEmpire.setAIinControl()
            myEmpire.player = '%s%s' % (myEmpire.myAIPlayer.name, myEmpire.myAIPlayer.id)
            myEmpire.password = 'ai4thewin'
        elif myEmpire.name != 'Neutral':
            chars = string.ascii_lowercase + string.digits
            pw = ''.join( random.choice(chars) for _ in range(8) )
            myEmpire.password = pw
            empireFile = open('%s.players' % self.galaxyName, 'a')
            message = "%s: EmpireID %s: %s : password: %s\n" % (myEmpire.name, myEmpire.id, player, pw)
            empireFile.write(message)
            empireFile.close()
    
    def genAIPlayer(self, myEmpire):
        """Create an AI Player in a galaxy, assign it to a random Empire"""
        id = self.myGalaxy.getNextID(self.myGalaxy.AIPlayers)
        d = {'id':id}
        myAI = ai.AIPlayer(d)
        myAI.setMyGalaxy(self.myGalaxy)
        myAI.setMyEmpire(myEmpire)
        myAI.setMyShipDesignsFromFile(self.dataPath)
        myAI.setMyDroneDesignsFromFile(self.dataPath)
    
    def genTech(self, empireID):
        """Actually Create Tech for Empire"""
        self.generateTech = GenerateTech(self.myGalaxy, self.dataPath, empireID)
        
    def genSystems(self):
        """Create the Systems, and connect them up"""
        self.generateSystems = GenerateSystems(self.myGalaxy, self.dataPath)
        self.myGalaxy.connectSystems()
    
    def genDataTypes(self):
        """Create the various data objects referenced by Galaxy"""
        self.generateDataTypes = GenerateDataTypes(self.myGalaxy, self.dataPath)
    
    def genDefaults(self):
        """Create the defaults for galaxy"""
        self.generateDefaultIndustry = GenerateDefaults(self.myGalaxy, self.dataPath)
    
    def genDesigns(self):
        """Create Ship and Drone Designs for Empires"""
        self.setTemplateData('shipDesigns.data')
        for empireID, myEmpire in self.myGalaxy.empires.iteritems():
            self.genDroneDesign(myEmpire)
            self.genShipDesign(myEmpire)
    
    def genDroneDesign(self, myEmpire):
        """Generate Drone Design for Empire"""
        droneIDs = funcs.sortStringList(self.myGalaxy.droneDesigns.keys())
        for key in droneIDs:
            droneDesignDict = self.myGalaxy.droneDesigns[key]
            myEmpire.genDroneDesign(droneDesignDict['name'], droneDesignDict['hull'], droneDesignDict['compDict'], droneDesignDict['weapDict'], 1)
    
    def genShipDesign(self, myEmpire):
        """Generate Drone Design for Empire"""
        shipIDs = funcs.sortStringList(self.myGalaxy.shipDesigns.keys())
        for key in shipIDs:
            shipDesignDict = self.myGalaxy.shipDesigns[key]
            myEmpire.genShipDesign(shipDesignDict['name'], shipDesignDict['hull'], shipDesignDict['compDict'], shipDesignDict['weapDict'], 1)
        for key, shipDesign in myEmpire.shipDesigns.iteritems():
            if 'Marine Transport' in shipDesign.name:
                shipDesign.obsolete = 1
    
    def genNeutralShips(self):
        """Build the default Neutral Ships that will protect Neutral Systems"""
        for systemID, self.currentSystem in self.myGalaxy.systems.iteritems():
            if self.currentSystem.myEmpireID == '0':
                self.genNeutralShipsAtSystem()

    def genNeutralShipsAtSystem(self):
        """Build the Neutral Ships based on city number"""
        num = (self.currentSystem.cities/5) * 3
        for i in range(num):
            shipDesignID = random.choice(self.myGalaxy.neutralShips[self.currentSystem.cities])
            self.genNeutralShipAtSystem(shipDesignID)
    
    def genNeutralShipAtSystem(self, shipDesignID):
        """Build a Ship at the current System"""
        x = random.randint(-20,20)
        y = random.randint(-20,20)
        myShip = self.currentSystem.addShip(1, '0', shipDesignID)
        myShip.setDesiredPosition(x,y)
        myShip.toSystem = self.currentSystem.id
        
class GenerateSystems(object):
    """Generate the Systems to be placed in Galaxy Object"""
    def __init__(self, galaxy, dataPath):
        self.myGalaxy = galaxy
        self.systemNames = []
        self.myGalaxy.systems = {}
        self.dataPath = dataPath
        self.numSystems = 1
        self.empireID = ''
        self.cityNum = 0
        self.x = 1
        self.y = 1
        self.posX = 0
        self.posY = 0
        self.myGalaxy.yMax = 0
        self.myGalaxy.xMax = 0
        self.maxWidth = 0
        self.maxHeight = 0
        self.setSystemNames()
        self.genSystems()
        self.setMax()
    
    def setSystemNames(self):
        """Set the System Names by reading the system name data file"""
        inputFile = self.dataPath + 'system_names.txt'
        self.systemNames = names.getNames(inputFile, 300)
    
    def genSystems(self):
        """Create the Systems"""
        for line in self.myGalaxy.genSystemsData:
            self.x = 1
            self.setSystemData(line)
            self.y += 1
            
    def setSystemData(self, line):
        """Set System Data by parsing the datafile given (eg. starMap4A.map)"""
        for character in line:
            (self.empireID, self.cityNum) = self.myGalaxy.genSystemsLegend[character]
            self.setupSystem()
    
    def setupSystem(self):
        """Only Create System if empireID is valid, either way increment position on map"""
        if not self.empireID:
            self.x += 1
        else:
            self.setPosX()
            self.setPosY()
            self.genSystem()
    
    def setPosX(self):
        """Set the System X Position"""
        self.posX = self.x * self.myGalaxy.systemSize
        self.setMaxWidth()
            
    def setMaxWidth(self):
        """Grow the Galaxy Max Width as systems are added in x"""
        if self.posX + self.myGalaxy.systemSize > self.maxWidth:
            self.maxWidth = self.myGalaxy.systemSize + self.posX
    
    def setPosY(self):
        """Set the System Y Position"""
        self.posY = self.y * self.myGalaxy.systemSize
        self.setMaxHeight()
            
    def setMaxHeight(self):
        """Grow the Galaxy Max Height as systems are added in y"""
        if self.posY + self.myGalaxy.systemSize > self.maxHeight:
            self.maxHeight = self.myGalaxy.systemSize + self.posY
    
    def genSystem(self):
        """Actually Create System"""
        d = {'id':str(self.numSystems), 'name':self.systemNames[self.numSystems], 
             'x':self.posX, 'y':self.posY, 'myEmpireID':self.empireID, 'cities':self.cityNum}
        mySystem = system.System(d)
        mySystem.setMyEmpire(self.myGalaxy.empires[self.empireID])
        mySystem.setMyGalaxy(self.myGalaxy)
        mySystem.setMyIndustry(self.myGalaxy.industrydata.keys())
        self.numSystems += 1
        self.x += 1
    
    def setMax(self):
        """Set the Galaxy x and y Max"""
        (self.myGalaxy.xMax, self.myGalaxy.yMax) = (self.maxWidth, self.maxHeight)

class GenerateTech(object):
    """Generate the Tech to be placed in Galaxy Object"""
    def __init__(self, galaxy, dataPath, empireID):
        self.myGalaxy = galaxy
        self.myEmpire = self.myGalaxy.empires[empireID]
        self.myEmpire.techTree = {}
        self.dataPath = dataPath
        self.techData = []
        self.setTechData()
        self.setTechTree()
    
    def setTechData(self):
        """Read the tech.csv file"""
        self.techData = open(self.dataPath + 'tech.csv').readlines()
    
    def setTechTree(self):
        """Populate the Tech Tree from techData"""
        for line in self.techData:
            self.parseTechLine(line)   
    
    def parseTechLine(self, line):
        """Go through each line and parse the information"""
        try:
            (id,name,x,y,complete,preTechs,preTechNum,requiredPoints,
            currentPoints,techAge,description) = string.split(line, '|')
            d = {'id':id, 'name':name, 'x':x, 'y':y, 'complete':complete, 'preTechs':preTechs,
                'preTechNum':preTechNum, 'requiredPoints':requiredPoints, 'currentPoints':currentPoints,
                'techAge':techAge, 'description':description[:-1]}
            myTech = tech.Tech(d)
            self.setMyTech(myTech)
        except:
            pass
    
    def setMyTech(self, myTech):
        """Set the tech to complete if desired by input file"""
        if int(myTech.id) in self.myGalaxy.startingTech:
            myTech.complete = 1
            myTech.currentPoints = myTech.requiredPoints
        myTech.x = myTech.x * globals.techSize
        myTech.y = myTech.y * globals.techSize
        self.myEmpire.techTree[myTech.id] = myTech

class GenerateDataTypes(object):
    """Generate the various Data Types from csv files to be placed in Galaxy Object"""
    def __init__(self, galaxy, dataPath):
        self.myGalaxy = galaxy
        self.dataPath = dataPath
        self.dataName = ''
        self.dataObjectDict = {}
        self.dataHeaders = []
        self.myDataObject = None
        self.genAllData()
    
    def genAllData(self):
        """Generate all the data types"""
        for dataname in ('regimentdata', 'industrydata', 'componentdata', 
                         'shiphulldata', 'dronehulldata', 'weapondata'):
            self.dataName = dataname
            self.clearOldData()
            self.genData()
            self.setDataToGalaxy()
    
    def clearOldData(self):
        """Clear the Data Headers and Data Rows"""
        self.dataObjectDict = {}
        self.dataHeaders = []
    
    def genData(self):
        """Based on the dataname grab the csv file and load data into Galaxy"""
        reader = self.openCSVFile()
        for row in reader:
            self.parseCSVRow(row)
        
    def openCSVFile(self):
        """Open the CSV file and return reader object for parsing"""
        filePath = self.dataPath + self.dataName + '.csv'
        return csv.reader(open(filePath, 'rb'))
    
    def parseCSVRow(self, row):
        """Go through each row of csv file"""
        if row[0] == 'id':
            self.dataHeaders = row
        else:
            self.genDataInput(row)
            self.setDataObjectToDict()
    
    def setDataObjectToDict(self):
        """Store the Data Object Created into Dictionary"""
        self.dataObjectDict[self.myDataObject.id] = self.myDataObject
    
    def genDataInput(self, row):
        """Create Data Input Dictionary d to use to gen Data Object"""
        d = {}
        num = 0
        for item in row:
            d[self.dataHeaders[num]] = item
            num += 1
        self.setMyDataObject(d)
    
    def setMyDataObject(self, d):
        """Create a Data Object given the data info from row of csv file"""
        self.myDataObject = None
        if self.dataName == 'regimentdata':
            self.myDataObject = regimentdata.RegimentData(d)
        elif self.dataName == 'industrydata':
            self.myDataObject = industrydata.IndustryData(d)
        elif self.dataName == 'componentdata':
            self.myDataObject = componentdata.ComponentData(d)
        elif self.dataName == 'shiphulldata':
            self.myDataObject = shiphulldata.ShipHullData(d)
        elif self.dataName == 'dronehulldata':
            self.myDataObject = shiphulldata.DroneHullData(d)
        elif self.dataName == 'weapondata':
            self.myDataObject = weapondata.WeaponData(d)
    
    def setDataToGalaxy(self):
        """Set the new Data to the Galaxy Object"""
        setattr(self.myGalaxy, self.dataName, self.dataObjectDict)
    
class GenerateDefaults(object):
    """Fill up the Galaxy with default objects"""
    def __init__(self, galaxy, dataPath):
        self.myGalaxy = galaxy
        self.dataPath = dataPath
        self.currentEmpireID = ''
        self.currentSystem = None
        self.genDefaultIndustry()
    
    def genDefaultIndustry(self):
        """Generate the default industry that each empire starts with"""
        for self.currentEmpireID, myEmpire in self.myGalaxy.empires.iteritems():
            if self.currentEmpireID == '0':
                self.genNeutralIndustry()
            else:
                myCaptialSystem = self.myGalaxy.getMyCaptialSystem(self.currentEmpireID)
                self.genPlayerIndustry(myCaptialSystem)
    
    def genPlayerIndustry(self, myCaptialSystem):
        """Generate the default industry on Captial System"""
        for key, num in self.myGalaxy.defaultIndustry.iteritems():
            myCaptialSystem.myIndustry[key] = num
        
    def genNeutralIndustry(self):
        """Build the default neutral industry"""
        for systemID, mySystem in self.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == self.currentEmpireID:
                num = mySystem.cities/5
                while num > 0:
                    mySystem.addIndustry(1,self.getMilitaIndustryType(mySystem.cities))
                    mySystem.citiesUsed += 2
                    num -= 1
                    
    def getMilitaIndustryType(self, cities):
        """Return the type of militia that neutral systems get based on size of system"""
        if cities >= 30:
            return '24'
        elif cities >= 20:
            return '23'
        else:
            return '22'