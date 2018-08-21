# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mainAdmin.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main application that runs ANW Admin
# ---------------------------------------------------------------------------
import wx
import string
import random
import types
import os
import csv

import mainNotebook
import galaxyPanel
import systemPanel
import empirePanel
import shipPanel
import regimentPanel
import anwp.func.storedata
import anwp.func.funcs
import anwp.func.names
import anwp.func.globals

class MainAdmin(wx.Frame):
    """The Main Admin Frame"""
    def __init__(self, parent, log, regen):
        wx.Frame.__init__(self, parent, -1, 'ANW Admin - version %s' % anwp.func.globals.currentVersion, size=(1024, 768))
        # set default values
        self.regen = regen
        self.log = log
        self.CenterOnScreen()
        self.CreateStatusBar()
        self.SetStatusText('Please Load a Galaxy')
        self.wildcard = 'anw files (*.anw)|*.anw|'    \
            'All files (*.*)|*.*'
        self.path = os.getcwd()[:-5]
        self.clientPath = '%s/Client/' % self.path
        self.dbPath = '%s/Database/' % self.path
        self.dataPath = '%s/Data/' % self.path
        self.workingGalaxy = None
        
        # prepare the menu bar
        menuBar = wx.MenuBar()

        # File Menu
        mnuFile = wx.Menu()
        mnuFile.Append(102, '&Open', 'Open an Existing Galaxy File')
        mnuSave = wx.Menu()
        mnuFile.Append(103, '&Save Galaxy', 'Save Galaxy to File')
        mnuFile.Append(999, '&Exit', 'Exit ANW Admin')
        menuBar.Append(mnuFile, '&File')

        # Generate Menu
        mnuGenerate = wx.Menu()
        mnuGenSystems = wx.Menu()
        mnuGenerate.Append(201, 'Generate &Galaxy', 'Generate Galaxy from scratch')
        mnuGenerate.Append(202, 'Generate &Test Battle', 'Test Ship Battle and Run it')
        menuBar.Append(mnuGenerate, '&Generate')
        
        # Admin Menu
        mnuAdmin = wx.Menu()
        mnuAdmin.Append(301, '&Force End Round-ANW1', 'Force the Server to end the Round')
        mnuAdmin.Append(302, '&Force End Round-ANW2', 'Force the Server to end the Round')
        mnuAdmin.Append(303, '&Force End Round-ANW3', 'Force the Server to end the Round')
        mnuAdmin.Append(304, '&Crowbar A', 'Crowbar A')
        menuBar.Append(mnuAdmin, '&Admin')

        # set the menu bar
        self.SetMenuBar(menuBar)
        
        # menu events
        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.onMenuHighlight)

        self.Bind(wx.EVT_MENU, self.mnuOpenGalaxy, id=102)
        self.Bind(wx.EVT_MENU, self.mnuSaveGalaxy, id=103)
        self.Bind(wx.EVT_MENU, self.mnuExitProgram, id=999)

        self.Bind(wx.EVT_MENU, self.mnuGenerateAll, id=201)
        self.Bind(wx.EVT_MENU, self.mnuGenerateBattle, id=202)
        
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound1, id=301)
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound2, id=302)
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound3, id=303)
        self.Bind(wx.EVT_MENU, self.mnuCrowbarA, id=304)

        # load notebook
        self.notebook = mainNotebook.MainNotebook(self, -1, log)
        # just to get the ships on opposites sides (well... try to at least)
        self.tmpPositionsIdx = [0,2,4,6,8,10,12,14,16,18,1,3,5,7,9,11,13,15,17,19]
        
        # auto-regen galaxy
        if regen == True:
            self.mnuGenerateAll(None)
            self.mnuExitProgram(None)
    
    def __set_properties(self):
        """Set the properties of the frame"""
        self.SetTitle('ANW Admin - version %s' % anwp.func.globals.currentVersion)

    def onMenuHighlight(self, event):
        # Show how to get menu item info from this event handler
        id = event.GetMenuId()
        item = self.GetMenuBar().FindItemById(id)
        if item:
            text = item.GetText()
            help = item.GetHelp()

        # but in this case just call Skip so the default is done
        event.Skip() 
    
    def mnuForceEndRound1(self, event):
        """Force the running Server to End its Round for current Galaxy"""
        from xmlrpclib import ServerProxy
        myServer = ServerProxy('http://localhost:8000')
        ##myServer = ServerProxy('http://www.armadanetwars.com:8000')
        adminPassword = 'hannah123'
        galaxyName = 'ANW1'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuForceEndRound2(self, event):
        """Force the running Server to End its Round for current Galaxy"""
        from xmlrpclib import ServerProxy
        myServer = ServerProxy('http://localhost:8000')
        ##myServer = ServerProxy('http://www.armadanetwars.com:8000')
        adminPassword = 'hannah123'
        galaxyName = 'ANW2'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuForceEndRound3(self, event):
        """Force the running Server to End its Round for current Galaxy"""
        from xmlrpclib import ServerProxy
        myServer = ServerProxy('http://localhost:8000')
        ##myServer = ServerProxy('http://www.armadanetwars.com:8000')
        adminPassword = 'hannah123'
        galaxyName = 'ANW3'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuCrowbarA(self, event):
        """Replace all existing ship battle objects with proper setup"""
        if self.workingGalaxy <> None:
            for battleID in self.workingGalaxy.shipBattles.keys():
                myShipBattle = self.workingGalaxy.shipBattles[battleID]
                if type(myShipBattle) <> types.StringType:
                    # save shipbattle to disk, replace value with shipbattle round
                    myShipBattle.setMyGalaxy(self.workingGalaxy)
                    myShipBattle.componentdata = None
                    myShipBattle.shiphulldata = None
                    myShipBattle.dronehulldata = None
                    myShipBattle.weapondata = None
                    anwp.func.storedata.saveToFile(myShipBattle, '%s/%s/%s.ship' % (self.dbPath, self.workingGalaxy.name, myShipBattle.id))
    
    def buildShips(self, myGalaxy, empireID, toSystem, shipDesigns, fromSystem):
        """Build ships from list of shipDesigns given to empire given"""
        mySystem = myGalaxy.systems[fromSystem]
        num = len(shipDesigns)
        x = 0
        y = 0
        
        for design in shipDesigns:
            x = random.randint(600,1400)
            y = random.randint(600,1400)
            myShip = mySystem.addShip(1, empireID, design)
            myShip.setDesiredPosition(x,y)
            myShip.toSystem = toSystem
            if empireID <> '1':
                myShip.myCaptain.addExperience(300)
            
    def mnuGenerateAll(self, event):
        """Generate Everything in order, do this in a quick and dirty fashion"""
        # generate galaxy
        if self.regen:
            templateFile = self.dataPath + 'starMap4A.py'
        else:
            templateFile = self.getTemplateFile()
            
        self.mnuGenerateGalaxy(event,0)
        self.mnuGenerateEmpires(templateFile,0)
        self.generateSystems(templateFile, 0)
        self.generateTech(self.dataPath + 'tech.csv', 0)
        for data in ('regimentdata', 'industrydata', 'componentdata', 'shiphulldata', 'dronehulldata',
                     'weapondata'):
            self.generateData(data, 0)
            
        self.generateDefaultIndustry()        
        
        # move from round 0 to round 1
        self.workingGalaxy.endRound()
        
        # gen the default ships for neutral protection
        self.generateDroneDesigns('1')
        self.generateShipDesigns('1')
        self.generateDefaultShips()
        
        # save default galaxy file
        anwp.func.storedata.saveToFile(self.workingGalaxy, self.dbPath + 'ANW.anw')
        self.saveClientData()
        
        # display result
        self.displayGalaxy(self.workingGalaxy)
        
    def mnuGenerateBattle(self, event):
        """Generate A Test Battle and run it"""
        # load the most recently generated galaxy
        self.loadGalaxyFromFile(self.dbPath + 'ANW.anw')
        
        if self.workingGalaxy == None:
            print 'Cannot load ANW.anw default galaxy'
            return
            
        # build default designs
        empireList = ['2','3']
        for id in empireList:
            self.generateDroneDesigns(id)
            self.generateShipDesigns(id)
        
        # build ship sims
        self.buildSimShips(empireList)
                
        # move from round 1 to round 2 to capture ship battle
        self.workingGalaxy.endRound()

    def mnuGenerateGalaxy(self, event, display=1):
        """Generate a Default Galaxy"""
        d = {'name':'ANW1', 'version':anwp.func.globals.currentVersion, 'systemSize':200, 'password':'', 'currentRound':0}
        myGalaxy = anwp.aw.galaxy.Galaxy(d)
        self.workingGalaxy = myGalaxy
        if display == 1:
            self.displayGalaxy(self.workingGalaxy)
        
    def mnuGenerateEmpires(self, templateFilePath, display=1):
        """Randomly Generate some Empires"""
        # load the template
        myDict = {}
        execfile(templateFilePath, globals(), myDict)
        self.__dict__.update(myDict)
        
        names = ('Neutral', 'Gaean Empire', 'Cronus Alliance', 'Rhean Federation', 'Hyperions', 'Themis Alliance', 'Iapetus Empire', 'Cruis Alliance', 'Phoebians', 'Mnemosynes')
        colors = (('ltpurple','dkpurple'),('yellow','dkgrey'),('cyan','dkpurple'),('white','dkblue'),('yellow','blood'),('white','blood'),('red','black'), ('green','dkgrey'), ('ltpurple','blood'), ('green', 'blood'))
        chosenColors = []
        for i in range(1,self.numEmpires+1):
            ##color1 = random.choice(('yellow','orange','green','cyan','red','pink','white','ltpurple','blue'))
            ##color2 = random.choice(('blood','dkgrey','dkpurple','dkgreen','dkblue','black'))
            ##color1 = colors[i-1][0]
            ##color2 = colors[i-1][1]
            
            colorIndex = 0
            while 1:
                colorIndex = random.randint(0,len(colors)-1)
                if colorIndex not in chosenColors:
                    chosenColors.append(colorIndex)
                    break
                
            color1 = colors[colorIndex][0]
            color2 = colors[colorIndex][1]
            d = {'id':i, 'name':names[i-1], 'password':'',
                 'color1':color1,
                 'color2':color2,
                 'imageFile':'emp_%s_%s_%s' % (str(i+1), color1, color2),
                 'CR':80000, 'viewResources':1, 'viewTradeRoutes':1}
            
            if d['id'] == 1:
                d['ai'] = 1
                d['password'] = 'pass'
                
            myEmpire = anwp.aw.empire.Empire(d)
            myEmpire.setMyGalaxy(self.workingGalaxy)
            myEmpire.myGalaxy.setCaptainNames()
            # set all diplomacy to 'No Relations'
            for j in range(1,self.numEmpires+1):
                myEmpire.setDiplomacy(str(j), 2)
                
        if display == 1:
            self.displayGalaxy(self.workingGalaxy)
    
    def generateShipDesigns(self, empireID):
        """Build Ship Designs for empire given"""
        # load ship design template
        templateFilePath = self.dataPath + 'shipDesigns.py'
        self.log.write('Building Ship designs from template=%s' % templateFilePath)
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        
        # load the template
        myDict = {}
        execfile(templateFilePath, globals(), myDict)
        self.__dict__.update(myDict)
        
        myEmpire = self.workingGalaxy.empires[empireID]
        shipIDs = anwp.func.funcs.sortStringList(myDict['shipDesigns'].keys())
        for key in shipIDs:
            value = myDict['shipDesigns'][key]
            myEmpire.genShipDesign(value['name'], value['hull'], value['compDict'], value['weapDict'], 1)
    
    def generateDroneDesigns(self, empireID):
        """Build Drone Designs for empire given"""
        # load drone design template
        templateFilePath = self.dataPath + 'shipDesigns.py'
        self.log.write('Building Drone designs from template=%s' % templateFilePath)
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        
        # load the template
        myDict = {}
        execfile(templateFilePath, globals(), myDict)
        self.__dict__.update(myDict)
        
        myEmpire = self.workingGalaxy.empires[empireID]
        droneIDs = anwp.func.funcs.sortStringList(myDict['droneDesigns'].keys())
        for key in droneIDs:
            value = myDict['droneDesigns'][key]
            myEmpire.genDroneDesign(value['name'], value['hull'], value['compDict'], value['weapDict'], 1)
    
    def buildSimShips(self, empireList):
        """Build up some Ships for the simulator to use"""
        # load galaxy
        if self.workingGalaxy == None:
            self.workingGalaxy = anwp.func.storedata.loadFromFile(self.dbPath + 'ANW1.anw')
        myGalaxy = self.workingGalaxy
        toSystem = '25'
        
        # build sim data for empires
        for empireID in empireList:
            fromSystem = str(int(empireID)*10)
            shipList = []
            for i in range(10):
                shipDesign = random.choice(('5','6','7','8'))
                shipList.append(shipDesign)
                        
            self.buildShips(myGalaxy, empireID, toSystem, shipList, fromSystem)
    
    def mnuGenerateTech(self, event, display=1):
        """ Read a tech.csv file to generate tech objects for all empires in a galaxy"""
        # open file
        self.log.write('Open Tech Template\n')
        wildcard = 'csv files (*.csv)|*.csv|'    \
            'All files (*.*)|*.*'
        dlg = wx.FileDialog(
            self, message='Choose a Tech Template File', defaultDir=self.dataPath, 
            defaultFile='', wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.log.write('%s\n' % path)
            self.generateTech(path, display)
            
        dlg.Destroy()

    def getTemplateFile(self):
        """get template file and path and return it for processing"""
        # open an Existing Galaxy File Template"""
        self.log.write('Open Galaxy Template\n')
        wildcard = 'py files (*.py)|*.py|'    \
            'All files (*.*)|*.*'
        dlg = wx.FileDialog(
            self, message='Choose a Galaxy Template File', defaultDir=self.dataPath, 
            defaultFile='', wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.log.write('%s\n' % path)
        dlg.Destroy()
        return path
            
    def mnuOpenGalaxy(self, event):
        """Open an Existing Galaxy File Dialog"""
        self.log.write('Open Galaxy File\n')
        dlg = wx.FileDialog(
            self, message='Choose a Galaxy DB File', defaultDir=self.dbPath, 
            defaultFile='', wildcard=self.wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.log.write('%s\n' % path)
            self.loadGalaxyFromFile(path)
            
        dlg.Destroy()
    
    def loadGalaxyFromFile(self, path):
        """Load Galaxy from File and display Galaxy Grid"""
        self.workingGalaxy = anwp.func.storedata.loadFromFile(path)
        if type(self.workingGalaxy) <> types.StringType:
            self.displayGalaxy(self.workingGalaxy)
        else:
            self.log.write(self.workingGalaxy)
            
    def displayGalaxy(self, galaxy):
        """Display Galaxy on Grid"""
        # Galaxy exists, populate galaxy grid
        self.log.write('Loading Galaxy:' + galaxy.name)
        self.SetStatusText('Galaxy:' + galaxy.name)
        
        # clear notebooks
        self.notebook.clearNotebooks()
        
        # add new notebooks
        self.notebook.galaxyNotebook = galaxyPanel.GalaxyPanel(self.notebook, -1, self.notebook.log, galaxy)
        self.notebook.AddPage(self.notebook.galaxyNotebook, 'galaxy')
        self.notebook.empireNotebook = empirePanel.EmpirePanel(self.notebook, -1, self.notebook.log, galaxy)
        self.notebook.AddPage(self.notebook.empireNotebook, 'empires')
        self.notebook.shipNotebook = shipPanel.ShipPanel(self.notebook, -1, self.notebook.log, galaxy)
        self.notebook.AddPage(self.notebook.shipNotebook, 'ships')
        self.notebook.regimentNotebook = regimentPanel.RegimentPanel(self.notebook, -1, self.notebook.log, galaxy)
        self.notebook.AddPage(self.notebook.regimentNotebook, 'regiments')
        self.notebook.systemNotebook = systemPanel.SystemPanel(self.notebook, -1, self.notebook.log, galaxy)
        self.notebook.AddPage(self.notebook.systemNotebook, 'systems')
            
    def mnuSaveGalaxy(self, event):
        """Save Galaxy to File"""
        # gather galaxy info
        path = self.dbPath
        cellData = self.notebook.galaxyNotebook.mainGrid.GetCellValues()
        name = self.notebook.galaxyNotebook.mainGrid.GetCellValue(0, 0)
        # is the Galaxy new?
        if self.workingGalaxy == None:
            # create new galaxy
            self.workingGalaxy = anwp.aw.galaxy.Galaxy(self.notebook.galaxyNotebook.mainGrid.GetDictValues(0))
            self.log.write('New Galaxy Created:' + name)
        elif self.checkGalaxyExists(name) == 0:
            # new galaxy with no file detected
            self.log.write('Galaxy:%s Created, but no Save File to modify' % name)
        else:
            # update existing Galaxy attributes
            self.log.write('Old Galaxy Detected:' + name)
            self.log.write('Update Galaxy Values:' + name)
            self.workingGalaxy.setAttributes(self.notebook.galaxyNotebook.mainGrid.GetDictValues(0))
        
        # Save Data from the Notebooks to the working galaxy
        self.notebook.galaxyNotebook.SaveData()
        self.notebook.empireNotebook.SaveData()
        self.notebook.shipNotebook.SaveData()
        self.notebook.regimentNotebook.SaveData()
        self.notebook.systemNotebook.SaveData()
        
        # save Galaxy back to file
        self.log.write('Saving Galaxy:' + name + ' to: ' + path)
        backup_dir = '%s%s/' % (path, name)
        dbPath = '%s%s.anw' % (backup_dir, name)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        result = anwp.func.storedata.saveToFile(self.workingGalaxy, dbPath)
        
        self.saveClientData()

        
    def saveClientData(self):
        """Save the client Data"""
        if self.workingGalaxy == None:
            return
        
        # save data files
        data = {'componentdata':self.workingGalaxy.componentdata, 
                'shiphulldata':self.workingGalaxy.shiphulldata,
                'dronehulldata':self.workingGalaxy.dronehulldata,
                'weapondata':self.workingGalaxy.weapondata,
                'regimentdata':self.workingGalaxy.regimentdata,
                'industrydata':self.workingGalaxy.industrydata}
        result = anwp.func.storedata.saveToFile(data, '%sclient.data' % self.dbPath)
        result = anwp.func.storedata.saveToFile(data, '%sclient.data' % self.clientPath)
    
    def checkGalaxyExists(self, name):
        """Check if Galaxy File exists in database"""
        path = '../Database/%s.anw' % name
        galaxy = anwp.func.storedata.loadFromFile(path)
        if type(galaxy) <> types.StringType:
            return 1
        else:
            self.log.write(galaxy)
            return 0
    
    def mnuRandomGenSystem(self, event):
        """Randomly Generate Systems"""
        self.log.write('Randomly Generate Systems\n')
    
    def mnuTemplateGenSystem(self, event, display=1):
        """Generate Systems from Template File"""
        # open an Existing Galaxy File Template"""
        self.log.write('Open Galaxy Template\n')
        wildcard = 'py files (*.py)|*.py|'    \
            'All files (*.*)|*.*'
        dlg = wx.FileDialog(
            self, message='Choose a Galaxy Template File', defaultDir=self.dataPath, 
            defaultFile='', wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.log.write('%s\n' % path)
            self.generateSystems(path, display)
            
        dlg.Destroy()
    
    def generateSystems(self, templateFilePath, display=1):
        """Take Template from FilePath and Generate Systems"""
        self.log.write('Building Systems from template=%s' % templateFilePath)
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        
        # load the template
        myDict = {}
        execfile(templateFilePath, globals(), myDict)
        self.__dict__.update(myDict)
        maxWidth = 0
        maxHeight = 0
        
        # clear previous systems
        self.workingGalaxy.systems = {}
        
        # create the systems
        listNames = anwp.func.names.getNames('system_names.txt',300,19)
        numSystems = 1
        y = 1
        
        for line in self.genSystemsData:
            x = 1
            for character in line:
                (empireID, cityNum) = self.genSystemsLegend[character]                
                if not empireID:
                    x += 1
                    continue
                # create system
                systemID = str(numSystems)
                
                posX = x * self.workingGalaxy.systemSize
                if posX + self.workingGalaxy.systemSize > maxWidth:
                    maxWidth = self.workingGalaxy.systemSize + posX
                    
                posY = y * self.workingGalaxy.systemSize
                if posY + self.workingGalaxy.systemSize > maxHeight:
                    maxHeight = self.workingGalaxy.systemSize + posY
                
                dict = {'id':systemID, 'name':listNames[numSystems], 'x':posX, 'y':posY, 'myEmpireID':empireID, 'cities':cityNum}
                newSystem = anwp.aw.system.System(dict)              
                newSystem.setMyEmpire(self.workingGalaxy.empires[empireID])
                newSystem.setMyGalaxy(self.workingGalaxy)
                numSystems += 1
                x+=1
            y += 1
        
        # update galaxy
        self.workingGalaxy.xMax = maxWidth
        self.workingGalaxy.yMax = maxHeight
        
        # connect systems
        self.workingGalaxy.connectSystems()
        
        # update grids
        if display == 1:
            self.displayGalaxy(self.workingGalaxy)
        
        return 1
    
    def generateData(self, data, display=1):
        """Take data name and generate data objects for galaxy from csv data file"""
        templateFilePath = self.dataPath + data + '.csv'
        self.log.write('Building %s Data from template=%s' % (data, templateFilePath))
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        myGalaxy = self.workingGalaxy
        
        # load industry data from file
        try:
            reader = csv.reader(open(templateFilePath, 'rb'))
        except:
            print 'error opening file for csv parsing'

        # populate the data objects for galaxy
        dataObject = {}
        dataColumns = []
        for row in reader:
            if row[0] == 'id':
                dataColumns = row
            else:
                d = {}
                num = 0
                for item in row:
                    d[dataColumns[num]] = item
                    num += 1
                    
                myData = None    
                
                if data == 'regimentdata':
                    myData = anwp.war.regimentdata.RegimentData(d)
                elif data == 'industrydata':
                    myData = anwp.aw.industrydata.IndustryData(d)
                elif data == 'componentdata':
                    myData = anwp.war.componentdata.ComponentData(d)
                elif data == 'shiphulldata':
                    myData = anwp.war.shiphulldata.ShipHullData(d)
                elif data == 'dronehulldata':
                    myData = anwp.war.shiphulldata.DroneHullData(d)
                elif data == 'weapondata':
                    myData = anwp.war.weapondata.WeaponData(d)
                
                dataObject[myData.id] = myData
        
        # set the dict in galaxy
        setattr(myGalaxy, data, dataObject)

        # update grids
        if display == 1:
            self.displayGalaxy(self.workingGalaxy)
        
        return 1

    def generateDefaultIndustry(self):
        """Generate the default industry that each Empire begins with"""
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        myGalaxy = self.workingGalaxy
        # find the capital System and populate it with default industry
        for empireID, myEmpire in myGalaxy.empires.iteritems():
            if empireID == '1':
                # build default neutral industry
                for systemID, mySystem in myGalaxy.systems.iteritems():
                    if mySystem.myEmpireID == empireID:
                        num = mySystem.cities/5
                        while num > 0:
                            mySystem.addIndustry(1,'25') # add a militia fortress
                            mySystem.citiesUsed += 2
                            num -= 1
            else:
                # for players, only provide industry on captial system, provide as optional
                myCaptialSystem = None
                for systemID, mySystem in myGalaxy.systems.iteritems():
                    if mySystem.myEmpireID == empireID:
                        if myCaptialSystem == None:
                            myCaptialSystem = mySystem
                        elif myCaptialSystem.cities < mySystem.cities:
                            myCaptialSystem = mySystem
                
                if myCaptialSystem <> None:
                    # populate player CapitalSystem with default industry
                    for item in self.defaultIndustry:
                        myEmpire.genIndustryOrder({'system':myCaptialSystem.id, 'round':1,
                                                   'type':'Add Industry','value':'%d-%s' % (item[0],item[1])})
                    myCaptialSystem.citiesUsed += self.citiesUsed

    def generateDefaultShips(self):
        """Generate all the default ships that will protect any Neutral Systems"""
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        myGalaxy = self.workingGalaxy
        myEmpire = self.workingGalaxy.empires['1']
        
        # build default neutral ships for each system owned by neutral empire
        for systemID, mySystem in myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == myEmpire.id:
                num = (mySystem.cities/5) * 3
                shipList = []
                for i in range(num):
                    # generate a default number of ships
                    shipDesign = random.choice(('1','2'))
                    shipList.append(shipDesign)
                
                self.buildShips(myGalaxy, myEmpire.id, systemID, shipList, systemID)
    
    def generateTech(self, templateFilePath, display=1):
        """Take Template from FilePath and Generate Tech"""
        self.log.write('Building Tech from template=%s' % templateFilePath)
        if self.workingGalaxy == 0:
            self.log.write('No Working Galaxy')
            return 0
        
        # load tech from file
        try:
            lines = open(templateFilePath).readlines()
        except:
            print 'error opening file'
        
        # populate tech for each empire
        for empireID, myEmpire in self.workingGalaxy.empires.iteritems():
            # clear the techTree
            myEmpire.techTree = {}
            
            # populate the techTree
            for line in lines:
                try:
                    (id,name,x,y,complete,preTechs,preTechNum,requiredPoints,
                     currentPoints,techAge,description) = string.split(line, '|')
                    
                    # this is for testing, the neutral player can have all tech
                    if empireID == '1':
                        complete = 1
                        currentPoints = requiredPoints
                        
                    d = {'id':id, 'name':name, 'x':x, 'y':y, 'complete':complete, 'preTechs':preTechs,
                         'preTechNum':preTechNum, 'requiredPoints':requiredPoints, 'currentPoints':currentPoints,
                         'techAge':techAge, 'description':description[:-1]}
                    myTech = anwp.aw.tech.Tech(d)
                    if int(id) in self.startingTech:
                        myTech.complete = 1
                        myTech.currentPoints = myTech.requiredPoints
                    myTech.getImageFileName()
                    myEmpire.techTree[id] = myTech
                except:
                    pass

        # update grids
        if display == 1:
            self.displayGalaxy(self.workingGalaxy)
        
        return 1

    def mnuExitProgram(self, event):
        """Close Program"""
        self.Close()
        
    def messageBox(self, message):
        """Popup a MessageBox"""
        dlg = wx.MessageDialog(self, message,
                               'ANW Admin Message',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-r', dest='regen', default=False,
                      action='store_true',
                      help='regenerate galaxy without loading gui')
    (options, args) = parser.parse_args()
    
    app = wx.PySimpleApp()
    frame = MainAdmin(None, sys.stdout, options.regen)
    frame.Show(True)
    app.MainLoop()



