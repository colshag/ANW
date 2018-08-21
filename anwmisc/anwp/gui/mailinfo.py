# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mailinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all galactic mail
# ---------------------------------------------------------------------------
import types

import pyui
import guibase

class MailInfoFrame(guibase.BaseFrame):
    """Displays Mail Information"""  
    def __init__(self, mode, app, title='Galactic Mail Service'):
        self.app = app
        self.width = 1024
        try:
            self.height = (app.height - mode.mainMenu.height - mode.mainFooter.height - 40) / 2
        except:
            self.height = (app.height - 120) / 2
        try:
            y = (mode.mainMenu.height)
        except:
            y = 40
        x = 0
            
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(MailInfoPanel(self))
    
class MailInfoPanel(guibase.BasePanel):
    """Panel for all Mail information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 11))
        
        # subject title
        self.lblMailRound = pyui.widgets.Label(text='PLEASE CHOOSE A ROUND TO VIEW MAIL:', type=1)
        self.addChild(self.lblMailRound, (0, 0, 8, 1))
        self.lstRounds = pyui.widgets.ListBox(self.onRoundSelected)

        # list of rounds to choose from
        d = {}
        try:
            self.currentRound = self.frame.mode.game.myGalaxy['currentRound']
            i = self.currentRound
            while i >= 1:
                d[i] = 'Round %d' % i
                i -= 1
        except:
            self.currentRound = 10
            i = self.currentRound
            while i >= 1:
                d[i] = 'Round %d' % i
                i -= 1
        self.populateListbox(self.lstRounds, d)
        self.addChild(self.lstRounds, (0, 1, 1, 10))

        # mail subject list
        self.lstMailSubjects = pyui.widgets.ListBox(self.onMailSelected)
        self.addChild(self.lstMailSubjects, (1, 1, 7, 10))
        self.populate()
        
        # pack widgets
        self.pack
    
    def populate(self):
        """Populate Message Subject List depending on round selected"""
        # mail subject list
        myMailSubjects = {}
        try:
            myMailBoxDict = self.frame.mode.game.myEmpire['mailBox']
            for id, mailBoxDict in myMailBoxDict.iteritems():
                if mailBoxDict['round'] == self.currentRound:
                    myMailSubjects[id] = mailBoxDict['subject']
        except:
            myMailSubjects = self.testDict

        self.populateListbox(self.lstMailSubjects, myMailSubjects)
    
    def onRoundSelected(self, item):
        """When a Round is selected all messages recieved in that round will be displayed"""
        if not item:
            pass
        else:
            self.currentRound = self.lstRounds.getSelectedItem().data
            self.populate()
    
    def onMailSelected(self, item):
        """When a mesage is selected the Message Body Frame is populated"""
        if not item:
            pass
        else:
            self.frame.mode.createMailBodyFrame(self.lstMailSubjects.getSelectedItem().data)
        
class MailBodyFrame(guibase.BaseFrame):
    """Displays Mail Body Frame"""  
    def __init__(self, mode, app, mailID):
        self.app = app
        self.id = mailID
        self.mode = mode
        try:
            self.myMailDict = self.mode.game.myEmpire['mailBox'][mailID]
            title = self.myMailDict['subject']
            messageType = self.myMailDict['messageType']
        except:
            self.myMailDict = {}
            title = 'Test Mail Subject Title'
            messageType = 'economic'
        try:
            self.simImagePath = app.simImagePath
        except:
            self.simImagePath = ''
        self.width = 1024
        try:
            self.height = (app.height - mode.mainMenu.height - mode.mainFooter.height - 40) / 2
        except:
            self.height = (app.height - 120) / 2
        try:
            y = (mode.mainMenu.height) + 20 + self.height
        except:
            y = 60 + self.height
        x = 0
            
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        if messageType == 'economics':
            self.setPanel(MailBodyEconomicPanel(self))
        elif messageType == 'industry':
            self.setPanel(MailBodyIndustryPanel(self))
        elif messageType == 'research':
            self.setPanel(MailBodyResearchPanel(self))
        elif messageType == 'trade':
            self.setPanel(MailBodyTradePanel(self))
        elif messageType == 'market':
            self.setPanel(MailBodyMarketPanel(self))
        elif messageType == 'army':
            self.setPanel(MailBodyArmyPanel(self))
        elif messageType == 'general':
            self.setPanel(MailBodyGeneralPanel(self))
        elif messageType == 'fleet':
            self.setPanel(MailBodyFleetPanel(self))
    
class MailBodyEconomicPanel(guibase.BasePanel):
    """Panel for all Economic Mail Status Information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 11))
        
        # empire and economic images
        try:
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, self.frame.mode.game.myEmpire['imageFile'])
        except:
            myEmpirePict = self.testImagePath + '1empire.png'
        
        self.pctMessageType = pyui.widgets.Picture('%seconomics.png' % (self.imagePath))
        self.addChild(self.pctMessageType, (0, 0, 1, 3))
        self.pctEmpire = pyui.widgets.Picture(myEmpirePict)
        self.addChild(self.pctEmpire, (0, 6, 1, 3))
        
        # message body
        self.lstMessageDesc = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstMessageDesc, (1, 0, 7, 11))
        try:
            myMessageDesc = {}
            i = 0
            for item in eval(self.frame.myMailDict['body']):
                if type(item) == types.StringType:
                    # add string as one item in description body list
                    myMessageDesc[i] = item
                    i += 1
                elif type(item) == types.ListType:
                    # break out list into its seperate items
                    for subitem in item:
                        myMessageDesc[i] = subitem
                        i += 1
        except:
            myMessageDesc = self.testDict
        self.populateListbox(self.lstMessageDesc, myMessageDesc)
        
        # pack widgets
        self.pack

class MailBodyIndustryPanel(MailBodyEconomicPanel):
    """Panel for Industry Mail Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%sindustry.png' % (self.imagePath))

class MailBodyResearchPanel(MailBodyEconomicPanel):
    """Panel for Research Mail Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%sresearch.png' % (self.imagePath))

class MailBodyTradePanel(MailBodyEconomicPanel):
    """Panel for Trade Mail Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%strade.png' % (self.imagePath))
    
class MailBodyMarketPanel(MailBodyEconomicPanel):
    """Panel for Market Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%smarket.png' % (self.imagePath))

class MailBodyArmyPanel(MailBodyEconomicPanel):
    """Panel for Army Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%sarmy_%s_%s.png' % (self.frame.app.simImagePath, self.frame.mode.game.myEmpire['color1'],
                                                              self.frame.mode.game.myEmpire['color2']))
class MailBodyFleetPanel(MailBodyEconomicPanel):
    """Panel for Fleet Status Information"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        self.pctMessageType.setFilename('%sarmada_%s_%s.png' % (self.frame.app.simImagePath, self.frame.mode.game.myEmpire['color1'],
                                                              self.frame.mode.game.myEmpire['color2']))
class MailBodyGeneralPanel(MailBodyEconomicPanel):
    """Panel for General Mail"""
    def __init__(self, frame):
        MailBodyEconomicPanel.__init__(self, frame)
        empireDict = self.frame.mode.game.allEmpires[self.frame.myMailDict['fromEmpire']]
        filename = '%s%s.png' % (self.frame.app.simImagePath, empireDict['imageFile'])
        self.pctMessageType.setFilename(filename)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Mail Info Panel')
    app = run.TestApplication(width, height)
    frame = MailInfoFrame(None, app)
    app.addGui(frame)
    frame2 = MailBodyFrame(None, app, '1')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
