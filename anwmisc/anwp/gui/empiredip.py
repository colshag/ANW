# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# empiredip.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows a user to view and modify diplomacy with another empire
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals
import anwp.func.funcs

class EmpireDipFrame(guibase.BaseFrame):
    """Basic Empire Diplomacy Frame, requires position, passes data to Panel"""  
    def __init__(self, mode, app, empireDict, x, y):
        self.app = app
        self.width = 320
        self.height = 330 # 11 * 30 down
        self.empireDict = empireDict
        title = empireDict['name']
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(EmpireDipPanel(self))

class EmpireDipPanel(guibase.BasePanel):
    """Empire Diplomacy Panel"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(4, 11))
        self.empireDict = self.frame.empireDict
        
        # title section
        self.lblStatus = pyui.widgets.Label('', type=1)
        self.addChild(self.lblStatus, (0, 0, 4, 1))
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (0, 1, 1, 3))
        self.btnIncrease = pyui.widgets.Button('Increase Relations', self.onIncrease)
        self.addChild(self.btnIncrease, (1, 1, 3, 1))
        self.btnDecrease = pyui.widgets.Button('Decrease Relations', self.onDecrease)
        self.addChild(self.btnDecrease, (1, 2, 3, 1))
        self.lblRelations = pyui.widgets.Label(text='Relations Detected', type=1)
        self.addChild(self.lblRelations, (0, 4, 4, 1))
        self.lblMyIntent = pyui.widgets.Label(text='My Intentions', type=1)
        self.addChild(self.lblMyIntent, (0, 5, 4, 1))
        self.lblRecentTitle = pyui.widgets.Label(text='MOST RECENT MESSAGE:', type=1)
        self.addChild(self.lblRecentTitle, (0, 6, 4, 1))
        self.lstMessage = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstMessage, (0, 7, 4, 2))
        self.slbAmount = pyui.widgets.SliderBar(None, 10000)
        self.addChild(self.slbAmount, (0, 9, 4, 1))
        self.btnSendCredits = pyui.widgets.Button('Send Credits', self.onSendCredits)
        self.addChild(self.btnSendCredits, (0, 10, 2, 1))
        self.btnSendMail = pyui.widgets.Button('Send Mail', self.onSendMail)
        self.addChild(self.btnSendMail, (2, 10, 2, 1))

        self.pack()
        self.populate()

    def buildRecentMessage(self):
        """Display the most recent message from Empire if any"""
        myMailBoxDict = self.frame.mode.game.myEmpire['mailBox']
        lastID = 0
        for id, mailBoxDict in myMailBoxDict.iteritems():
            if int(id) > int(lastID) and mailBoxDict['fromEmpire'] == self.empireDict['id']:
                lastID = id
                
        if lastID <> 0:
            mailBoxDict = myMailBoxDict[lastID]
            s = ''
            body = eval(mailBoxDict['body'])
            for item in body:
                s = s + item
            return (s, mailBoxDict['round'])
        
        return ('', 0)

    def clearAll(self):
        """clear items"""
        self.btnSendCredits.disable()
        self.btnIncrease.enable()
        self.btnDecrease.enable()
        self.btnSendMail.enable()
        self.slbAmount.setValue(1)

    def onIncrease(self, item):
        """Increase Relations"""
        try:
            serverResult = self.frame.mode.game.server.increaseDiplomacy(self.frame.mode.game.authKey, self.empireDict['id'])
            if serverResult == 1:
                self.frame.mode.game.myEmpire['diplomacy'][self.empireDict['id']]['myIntent'] = 'increase'
                self.populate()
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onIncrease->Connection to Server Lost, Login Again')
    
    def onDecrease(self, item):
        """Decrease Relations"""
        try:
            serverResult = self.frame.mode.game.server.decreaseDiplomacy(self.frame.mode.game.authKey, self.empireDict['id'])
            if serverResult == 1:
                self.frame.mode.game.myEmpire['diplomacy'][self.empireDict['id']]['myIntent'] = 'decrease'
                self.populate()
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onDecrease->Connection to Server Lost, Login Again')
    
    def onSendCredits(self, item):
        """Send Credits to Empire"""
        try:
            serverResult = self.frame.mode.game.server.sendCredits(self.frame.mode.game.authKey, self.empireDict['id'], self.slbAmount.position)
            if serverResult == 1:
                self.frame.mode.game.myEmpire['CR'] -= self.slbAmount.position
                self.frame.mode.modeMsgBox('%d CREDITS Sent to %s' % (self.slbAmount.position, self.empireDict['name']))
                self.frame.mode.mainFooter.panel.populate()
                self.populate()
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onSendCredits->Connection to Server Lost, Login Again')
    
    def onSendMail(self, item):
        """Send Mail to Empire"""
        self.frame.mode.createSendMailFrame(self.empireDict)
    
    def populate(self):
        """Populate items"""
        self.clearAll()
        myRecentMessage = ''
        myRecentRound = 0
        credits = 0
        
        try:
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, self.empireDict['imageFile'])
            (myRecentMessage, myRecentRound) = self.buildRecentMessage()
            relations = self.frame.mode.game.myEmpire['diplomacy'][self.empireDict['id']]['empireIntent']
            intent = self.frame.mode.game.myEmpire['diplomacy'][self.empireDict['id']]['myIntent']
            credits = self.frame.mode.game.myEmpire['CR']
            self.frame.title = '%s' % self.empireDict['name']
            self.lblStatus.setText(anwp.func.globals.diplomacy[self.frame.mode.game.myEmpire['diplomacy'][self.empireDict['id']]['diplomacyID']]['name'])
        except:
            # this allows for testing panel outside game
            myEmpirePict = self.testImagePath + 'empire1.png'
            relations = 'none'
            intent = 'none'
            self.lblStatus.setText('No Relations')
            
        # recent message
        if myRecentMessage <> '':
                self.lblRecentTitle.setText('LAST MESSAGE IN ROUND: %d' % myRecentRound)
                recentMessage = anwp.func.funcs.returnDictFromString(myRecentMessage, 25)
                self.populateListbox(self.lstMessage, recentMessage)
        else:
            self.lblRecentTitle.setText('NO MESSAGES RECIEVED')
            self.lstMessage.clear()
        
        # send credits
        if credits > 0:
            self.slbAmount.setRange(credits)
            self.btnSendCredits.enable()
        else:
            self.slbAmount.setRange(1)
            self.btnSendCredits.disable()
        
        # empire pict
        self.pctEmpire.setFilename(myEmpirePict)
        
        # colorize current level of diplomacy
        if self.lblStatus.text == anwp.func.globals.diplomacy[1]['name']:
            self.lblStatus.setColor(anwp.func.globals.colors['red'])
            self.btnDecrease.disable()
        elif self.lblStatus.text == anwp.func.globals.diplomacy[2]['name']:
            self.lblStatus.setColor(anwp.func.globals.colors['yellow'])
        elif self.lblStatus.text == anwp.func.globals.diplomacy[3]['name']:
            self.lblStatus.setColor(anwp.func.globals.colors['ltpurple'])
        elif self.lblStatus.text == anwp.func.globals.diplomacy[4]['name']:
            self.lblStatus.setColor(anwp.func.globals.colors['blue'])
        elif self.lblStatus.text == anwp.func.globals.diplomacy[5]['name']:
            self.lblStatus.setColor(anwp.func.globals.colors['dkgreen'])
        else:
            self.lblStatus.setColor(anwp.func.globals.colors['green'])
            self.btnIncrease.disable()
        
        # relations detected
        if relations == 'increase':
            self.lblRelations.setText('Increased Relations Detected')
            self.lblRelations.setColor(anwp.func.globals.colors['green'])
        else:
            self.lblRelations.setText('No Increased Relations Detected')
            self.lblRelations.setColor(anwp.func.globals.colors['black'])
        
        # my intent detected
        if intent == 'increase':
            self.lblMyIntent.setText('Submitted to Increase Relations')
            self.lblMyIntent.setColor(anwp.func.globals.colors['green'])
        elif intent == 'decrease':
            self.lblMyIntent.setText('Submitted to Descrease Relations')
            self.lblMyIntent.setColor(anwp.func.globals.colors['red'])
        else:
            self.lblMyIntent.setText('No Relation Change Wanted')
            self.lblMyIntent.setColor(anwp.func.globals.colors['black'])
        
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    empireDict = {'id':'1', 'name':'Test Empire'}
    pyui.init(width, height, 'p3d', 0, 'Testing EmpireDip Panel')
    app = run.TestApplication(width, height)
    frame = EmpireDipFrame(None, app, empireDict, 10, 10)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
