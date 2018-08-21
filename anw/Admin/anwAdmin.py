# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# anwAdmin.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main application that runs ANW Admin
# ---------------------------------------------------------------------------
import xmlrpclib
import wx
import string
import random
import types
import os
import csv

from pandac.PandaModules import Filename
import mainNotebook
import galaxyPanel
import systemPanel
import empirePanel
import shipPanel
import regimentPanel
from anw.func import storedata, funcs, names, globals
from anw.admin import generate
from anw.aw import galaxy

class MainAdmin(wx.Frame):
    """The Main Admin Frame"""
    def __init__(self, parent, log, regen):
        wx.Frame.__init__(self, parent, -1, 'ANW Admin - version %s' % globals.currentVersion, size=(1024, 768))
        # set default values
        self.regen = regen
        self.log = log
        self.CenterOnScreen()
        self.CreateStatusBar()
        self.SetStatusText('Please Load a Galaxy')
        self.wildcard = 'anw files (*.anw)|*.anw|'    \
            'All files (*.*)|*.*'
        self.path = os.path.abspath(sys.path[0])[:-5]
        self.pandapath = Filename.fromOsSpecific(self.path).getFullpath()
        self.clientPath = '%s/Client/' % self.path
        self.dbPath = '%s/Database/' % self.path
        self.dataPath = '%s/Data/' % self.path
        self.adminPath = '%s/Admin/' % self.path
        self.serverPath = '%s/Server/' % self.path
        self.workingGalaxy = None
        self.generateGalaxy = None
        
        # prepare the menu bar
        menuBar = wx.MenuBar()

        # File Menu
        mnuFile = wx.Menu()
        mnuFile.Append(102, '&Open', 'Open an Existing Galaxy File')
        mnuFile.Append(103, '&Save Galaxy', 'Save Galaxy to File')
        mnuFile.Append(999, '&Exit', 'Exit ANW Admin')
        menuBar.Append(mnuFile, '&File')

        # Generate Local
        mnuLocal = wx.Menu()
        mnuLocal.Append(200, 'Generate Player File From GAE', 'Get a list of all registered players from google')
        mnuLocal.Append(201, 'Generate Galaxy', 'Generate Galaxy from scratch')
        mnuLocal.Append(210, 'Submit Galaxy to GAE', 'Submit Galaxy to Google')
        mnuLocal.Append(220, 'Submit Game Results to GAE', 'Submit Game to Google')
        menuBar.Append(mnuLocal, 'Local Tasks')
        
        # Admin Menu
        mnuAdmin = wx.Menu()
        mnuAdmin.Append(301, '&Force End Round-ANW1-localhost', 'Force the Server to end the Round')
        mnuAdmin.Append(302, '&Force End Round-ANW4-localhost', 'Force the Server to end the Round')
        mnuAdmin.Append(303, '&Force End Round-ANW5-localhost', 'Force the Server to end the Round')
        mnuAdmin.Append(304, '&Send Ship Designs to File', 'Scrape Ship Designs')
        menuBar.Append(mnuAdmin, '&Admin')

        # Submit Production
        mnuProd = wx.Menu()
        mnuProd.Append(400, 'Generate Player File From GAE', 'Get a list of all registered players from google')
        mnuProd.Append(410, 'Submit Galaxy to GAE', 'Submit Galaxy to Google')
        mnuProd.Append(420, 'Email Players Login Info', 'Email All Players their Login Information')
        mnuProd.Append(430, 'Submit Game Results to GAE', 'Submit Game to Google')
        menuBar.Append(mnuProd, 'Production Tasks')
        
        # Submit Other
        #mnuOther = wx.Menu()
        #mnuOther.Append(500, 'Submit game info to Starcraft Ladder', 'jabronie!')
        #mnuOther.Append(501, 'Generate Weekly Matches, email to colshag', 'jabronie!')
        #menuBar.Append(mnuOther, 'Other Tasks')
        
        # set the menu bar
        self.SetMenuBar(menuBar)
        
        # menu events
        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.onMenuHighlight)

        self.Bind(wx.EVT_MENU, self.mnuOpenGalaxy, id=102)
        self.Bind(wx.EVT_MENU, self.mnuSaveGalaxy, id=103)
        self.Bind(wx.EVT_MENU, self.mnuExitProgram, id=999)

        self.Bind(wx.EVT_MENU, self.mnuSavePlayerFile, id=200)
        self.Bind(wx.EVT_MENU, self.mnuGenerateGalaxy, id=201)
        self.Bind(wx.EVT_MENU, self.mnuSubmitGalaxyToGAE, id=210)
        self.Bind(wx.EVT_MENU, self.mnuSubmitGameToGAE, id=220)
        
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound1, id=301)
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound4, id=302)
        self.Bind(wx.EVT_MENU, self.mnuForceEndRound5, id=303)
        self.Bind(wx.EVT_MENU, self.mnuScrapeShipDesigns, id=304)
        
        self.Bind(wx.EVT_MENU, self.mnuSavePlayerFileProd, id=400)
        self.Bind(wx.EVT_MENU, self.mnuSubmitGalaxyToGAEProd, id=410)
        self.Bind(wx.EVT_MENU, self.mnuEmailPlayers, id=420)
        self.Bind(wx.EVT_MENU, self.mnuSubmitGameToGAEProd, id=430)
        
        self.Bind(wx.EVT_MENU, self.mnuSubmitOtherToProd, id=500)
        self.Bind(wx.EVT_MENU, self.mnuGenerateMatches, id=501)

        # load notebook
        self.notebook = mainNotebook.MainNotebook(self, -1, log)
        # just to get the ships on opposites sides (well... try to at least)
        self.tmpPositionsIdx = [0,2,4,6,8,10,12,14,16,18,1,3,5,7,9,11,13,15,17,19]
        
        # auto-regen galaxy
        if regen == True:
            self.mnuGenerateGalaxy(None)
            self.mnuExitProgram(None)
    
    def __set_properties(self):
        """Set the properties of the frame"""
        self.SetTitle('ANW Admin - version %s%s' % (globals.currentVersion,globals.currentVersionTag))

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
        adminPassword = 'hannah123'
        galaxyName = 'ANW1'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuForceEndRound4(self, event):
        """Force the running Server to End its Round for current Galaxy"""
        from xmlrpclib import ServerProxy
        myServer = ServerProxy('http://localhost:8000')
        adminPassword = 'hannah123'
        galaxyName = 'ANW4'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuForceEndRound5(self, event):
        """Force the running Server to End its Round for current Galaxy"""
        from xmlrpclib import ServerProxy
        myServer = ServerProxy('http://localhost:8000')
        adminPassword = 'hannah123'
        galaxyName = 'ANW5'
        key = {'adminPassword':adminPassword, 'galaxyName':galaxyName}
        myServer.forceEndRound(key)
    
    def mnuScrapeShipDesigns(self, event):
        """Replace all existing ship battle objects with proper setup"""
        shipDesignList = []
        droneDesignList = []
        chosenEmpireToScrapeID = '1'
        if self.workingGalaxy != None:
            for empireID, myEmpire in self.workingGalaxy.empires.iteritems():
                if empireID == chosenEmpireToScrapeID:
                    for designID in funcs.sortStringList(myEmpire.shipDesigns.keys()):
                        myShipDesign = myEmpire.shipDesigns[designID]
                        myDesign = myShipDesign.getMyDesign()
                        shipDesignList.append((myDesign[0], myDesign[1],myDesign[2],myDesign[3]))
                    for designID in funcs.sortStringList(myEmpire.droneDesigns.keys()):
                        myDroneDesign = myEmpire.droneDesigns[designID]
                        myDesign = myDroneDesign.getMyDesign()
                        droneDesignList.append((myDesign[0], myDesign[1],myDesign[2],myDesign[3]))
        result = storedata.saveToFile(shipDesignList, '%sshipdesigns.ai' % self.dataPath)
        result = storedata.saveToFile(droneDesignList, '%sdronedesigns.ai' % self.dataPath)
        result = storedata.printListToFile(shipDesignList, '%sshipdesigns.txt' % self.dataPath)
        
    def mnuGenerateGalaxy(self, event):
        """Generate Galaxy and Display"""
        mapFilename = self.getMapFileName()
        self.setWorkingGalaxy(mapFilename)
        self.displayGalaxy(self.workingGalaxy)
        
    def setWorkingGalaxy(self, mapFile):
        """Generate Galaxy"""
        self.generateGalaxy = generate.GenerateGalaxy()
        playerList = self.getPlayerList()
        self.generateGalaxy.genGalaxy(self.dataPath, mapFile, playerList, doAI=1)
        self.workingGalaxy = self.generateGalaxy.getGalaxy()
    
    def getPlayerList(self):
        try:
            f = open(self.getPlayerListFile(), 'r')
            s = f.readline()
            myList = eval(s)
            return myList
        except:
            print 'could not read playerlist.txt'
    
    def getPlayerListFile(self):
        """Open an Existing Player File"""
        return 'playerlist.txt'
        ##self.log.write('Open Player File\n')
        ##fileName = ''
        ##dlg = wx.FileDialog(
            ##self, message='Choose a Player File', defaultDir=self.adminPath, 
            ##defaultFile='playerlist.txt', wildcard='txt files (*.txt)|*.txt|', style=wx.OPEN | wx.CHANGE_DIR
            ##)
        ##if dlg.ShowModal() == wx.ID_OK:
            ##fileName = dlg.GetFilename()
            
        ##dlg.Destroy()
        ##return fileName
            
    def getMapFileName(self):
        """Open an Existing Galaxy File Dialog"""
        return 'starMap4A.map'
        ##self.log.write('Open Map File\n')
        ##mapFileName = ''
        ##dlg = wx.FileDialog(
            ##self, message='Choose a Map DB File', defaultDir=self.dataPath, 
            ##defaultFile='starMap4A.map', wildcard='map files (*.map)|*.map|', style=wx.OPEN | wx.CHANGE_DIR
            ##)
        ##if dlg.ShowModal() == wx.ID_OK:
            ##mapFileName = dlg.GetFilename()
            
        ##dlg.Destroy()
        ##return mapFileName
    
    def mnuGenerateBattleFromFile(self, event):
        """Generate A Test Battle from file and run it"""
        self.setWorkingGalaxy('starMap4A.map')
        myShipBattle = storedata.loadFromFile('../Database/ANW1/1.ship')
        self.runBattle(myShipBattle)
    
    def getShipBattleFileName(self):
        """Open an Existing Ship Battle File"""
        self.log.write('Open Ship Battle File\n')
        mapFileName = ''
        dlg = wx.FileDialog(
            self, message='Choose a Ship Battle File', defaultDir=self.dbPath, 
            defaultFile='1.ship', wildcard='ship files (*.ship)|*.ship|', style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            shipBattleFileName = dlg.GetFilename()
            
        dlg.Destroy()
        return shipBattleFileName
    
    def runBattle(self, myShipBattle):
        """Run the Battle for viewing"""
        from anw.client.directapp import DirectApplication
        myApp = DirectApplication(1,'','','','',myShipBattle)
        myApp.loadGame()
        run()
    
    def buildSimShips(self, empireID, shipList, toSystem):
        """Build up some Ships for the simulator to use"""
        x = -10
        fromSystem = empireID
        for i in range(10):
            shipDesignID = random.choice(shipList)
            self.buildShip(empireID, shipDesignID, toSystem, fromSystem, x)
            x += 2
    
    def buildShip(self, empireID, shipDesignID, toSystem, fromSystem, x):
        """Build some ships for Galaxy"""
        mySystem = self.workingGalaxy.systems[fromSystem]
        myShip = mySystem.addShip(1, empireID, shipDesignID)
        size = int(globals.battlemapQuadSize)/2
        myShip.setDesiredPosition(random.randint(0,size),
                                  random.randint(0,size))
        myShip.toSystem = toSystem
            
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
        self.workingGalaxy = storedata.loadFromFile(path)
        if type(self.workingGalaxy) != types.StringType:
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
            self.workingGalaxy = galaxy.Galaxy(self.notebook.galaxyNotebook.mainGrid.GetDictValues(0))
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
        
        result = storedata.saveToFile(self.workingGalaxy, dbPath)
        
        self.saveClientData()

    def mnuSavePlayerFile(self, event):
        """Retrieve list of active players from google store as file"""
        try:
            s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
            result = s.app.getAllPlayers()
            try:
                f = open('playerlist.txt', 'w')
                f.write(str(result))
                f.close()
            except:
                print 'Unable to Save File'
            return result
        except:
            return 0
    
    def mnuSavePlayerFileProd(self, event):
        """Retrieve list of active players from google store as file"""
        try:
            s = xmlrpclib.Server('http://anetwars.appspot.com/xmlrpc/')
            result = s.app.getAllPlayers()
            try:
                f = open('playerlist.txt', 'w')
                f.write(str(result))
                f.close()
            except:
                print 'Unable to Save File'
            return result
        except:
            return 0
        
    def mnuSubmitGalaxyToGAE(self, event):
        """Submit the Galaxy information to Google"""
        try:
            s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
            myPlayers = self.getMyPlayers()
            result = s.app.createGalaxy(self.workingGalaxy.name,
                                    len(self.workingGalaxy.empires),
                                    myPlayers,
                                    self.workingGalaxy.maxHoursLeft)
            return result
        except:
            return 0
    
    def mnuSubmitGameToGAE(self, event):
        """Submit the game information to Google"""
        try:
            if self.workingGalaxy == None:
                return
            d = {}
            s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
            playerDict = self.getPlayerInfo()
            result = s.app.submitGame(self.workingGalaxy.name,
                                    playerDict,
                                    self.workingGalaxy.currentRound)
            return result
        except:
            return 0
    
    def mnuSubmitGameToGAEProd(self, event):
        """Submit the game information to Google"""
        try:
            if self.workingGalaxy == None:
                return
            d = {}
            s = xmlrpclib.Server('http://anetwars.appspot.com/xmlrpc/')
            playerDict = self.getPlayerInfo()
            result = s.app.submitGame(self.workingGalaxy.name,
                                    playerDict,
                                    self.workingGalaxy.currentRound)
            return result
        except:
            return 0

    def mnuSubmitOtherToProd(self, event):
        try:
            # 'jason.ewasiuk@gmail.com'
            # 'jefflewis12@gmail.com'
            # 'how23fadeaway@gmail.com'
            # 'zhaoiang@gmail.com'
            # 'ImpulseMT@gmail.com'
            # 'richard.ung@gmail.com'
            # 'shockwave_3000@hotmail.com'
            # 'mahmad8@gmail.com'
            # 'BryceHannigan@gmail.com'
            # 'lyh_87@hotmail.com'
            # 'colshag@gmail.com'
            # 'sppyster@gmail.com'
            # 'darren.yu@gmail.com'
            # 'davidluong5@gmail.com'
            # 'kansny@gmail.com'
            # 'philipkmartin@gmail.com'
            # 'gumshoes@gmail.com'
            # 'nyst306@gmail.com'
            # 'GeoffreyCTan@gmail.com'
            # 'cjec21@gmail.com'
            # 'Kings888@gmail.com'
            
            import datetime
            winner = ''
            loser = ''
            map = 'Blistering Sands'
            
            playerDict = {winner:{'experience':1000, 'win':1},
                          loser:{'experience':250, 'win':0}
                          }
            ##s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
            s = xmlrpclib.Server('http://starcraft2ladder.appspot.com/xmlrpc/')
            result = s.app.submitGame(playerDict)
            result = s.app.createGame(datetime.date.today().strftime("%A %d. %B %Y"),
                                      map,
                                      str([winner, loser]),
                                      str([winner]))
            return result
        except:
            return 0
    
    def mnuGenerateMatches(self, event):
        try:
            ##s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
            s = xmlrpclib.Server('http://starcraft2ladder.appspot.com/xmlrpc/')

            playerDict = s.app.getAllPlayers()
            gamesPlayed = s.app.getAllGamesPlayed()
            maps = ['Blistering Sands',
                    'Scrap Station',
                    'XelNaga Caverns',
                    'Kulas Ravine',
                    'Lost Temple',
                    'Metalopolis',
                    'Deltra Quadrant'
                    ]
            
            played_maps = ['Desert Oasis','Steppes of War','Kulas Ravine']
            
            WSA = self.getPlayersFromClan(playerDict, 'WSA')
            ENB = self.getPlayersFromClan(playerDict, 'ENB')
                   
            body = 'ES2L for Week %s:\n\n' % funcs.getTodaysDateAsString()
            body = body + 'The Map we will be playing 2 games on for each pairing is: %s\n\n' % random.choice(maps)
            body = body + 'Below are the random pairings:\n\n'
            body = body + '---==========================================================---\n'
                        
            while (ENB != []):
                if WSA != [] and ENB != []:
                    player1 = random.choice(WSA)
                    player2 = random.choice(ENB)
                    email1 = playerDict[player1]
                    email2 = playerDict[player2]
                    if self.haveTheyAlreadyPlayed(gamesPlayed, email1, email2) == 0:
                        WSA.remove(player1)
                        ENB.remove(player2)
                        body = body + '%s   VS   %s\n' % (player1, player2)
                elif WSA == [] and len(ENB) > 1:
                    player1 = random.choice(ENB)
                    player2 = random.choice(ENB)
                    email1 = playerDict[player1]
                    email2 = playerDict[player2]
                    if self.haveTheyAlreadyPlayed(gamesPlayed, email1, email2) == 0:
                        ENB.remove(player1)
                        ENB.remove(player2)
                        body = body + '%s   VS   %s\n' % (player1, player2)

            self.emailResultsToAdmin(body)
            return 1
        except:
            return 0
    
    def haveTheyAlreadyPlayed(self, gamesPlayed, email1, email2):
        for game in gamesPlayed:
            if email1 in game and email2 in game:
                return 1
        return 0
     
    def getPlayersFromClan(self, playerDict, clanID):
        playerList = []
        for name in playerDict.keys():
            if name[1:4] == clanID:
                playerList.append(name)
        return playerList
    
    def emailResultsToAdmin(self, body):
        subject = 'ES2L Results for Week:%s' % funcs.getTodaysDateAsString()
        to = 'colshag@gmail.com'
        funcs.sendMail(to, subject, body)
        
    def getPlayerInfo(self):
        """Return Player info as a dict with key being player email"""
        d = {}
        for empireID, myEmpire in self.workingGalaxy.empires.iteritems():
            if empireID != '0' and myEmpire.player != '':
                d[myEmpire.player] = {'experience':myEmpire.experience,
                                       'delay':myEmpire.delay,
                                       'win':myEmpire.alive}
        return d
        
    def mnuSubmitGalaxyToGAEProd(self, event):
        """Submit the Galaxy information to Google"""
        try:
            s = xmlrpclib.Server('http://anetwars.appspot.com/xmlrpc/')
            myPlayers = self.getMyPlayers()
            result = s.app.createGalaxy(self.workingGalaxy.name,
                                    len(self.workingGalaxy.empires),
                                    myPlayers,
                                    self.workingGalaxy.maxHoursLeft)
            return result
        except:
            return 0
    
    def mnuEmailPlayers(self, event):
        """Email Players their login information"""
        try:
            subject = 'Welcome to Armada Net Wars, %s game has begun!' % self.workingGalaxy.name
            for id, myEmpire in self.workingGalaxy.empires.iteritems():
                if id != '0':
                    to = myEmpire.emailAddress
                    text = """
                    Thank you for trying out Armada Net Wars,

                    Please go to www.armadanetwars.com->tutorials to get online video help on how to play.
                    
                    This email signifies that you have been officially invited to play a sanctioned ladder game.
                    If this email is in error, please email colshag@gmail.com to fix this mistake.
                    
                    Here is your login information:
                    
                    GameID: %s
                    
                    EmpireID: %s
                    
                    Empire Name: %s
                    
                    Password: (This is your unique password, contact our admin if you forgot what this is when you created your account)
                    
                    Server: http://www.armadanetwars.com:8000
                    
                    Please try and do your game turn once a day, if you are the last person to do your turn, please try and do your next turn
                    that same day when the next turn is ready (should be less then one minute).
                    """ % (self.workingGalaxy.name, id, myEmpire.name)
                    funcs.sendMail(to, subject, text)
        except:
            return 0
    
    def getMyPlayers(self):
        myPlayers = []
        for id, myEmpire in self.workingGalaxy.empires.iteritems():
            if id != '0':
                myPlayers.append(myEmpire.player)
        random.shuffle(myPlayers)
        return str(myPlayers)
        
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
        result = storedata.saveToFile(data, '%sclient.data' % self.dbPath)
        result = storedata.saveToFile(data, '%sclient.data' % self.clientPath)
        result = storedata.saveToFile(data, '%sclient.data' % self.adminPath)
        result = storedata.saveToFile(data, '%sclient.data' % self.serverPath)
    
    def checkGalaxyExists(self, name):
        """Check if Galaxy File exists in database"""
        path = '../Database/%s/%s.anw' % (name, name)
        galaxy = storedata.loadFromFile(path)
        if galaxy == None:
            return 0
        elif type(galaxy) != types.StringType:
            return 1
        else:
            self.log.write(galaxy)
            return 0
    
    def mnuRandomGenSystem(self, event):
        """Randomly Generate Systems"""
        self.log.write('Randomly Generate Systems\n')
    
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



