# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# configinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays User Config information
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals

class ConfigInfoFrame(guibase.BaseFrame):
    """Displays User Config Information"""  
    def __init__(self, mode, app, title='User Configuration'):
        self.app = app
        self.width = 1024
        try:
            self.height = (app.height - mode.mainMenu.height - mode.mainFooter.height - 40)
        except:
            self.height = (app.height - 120)
        try:
            y = (mode.mainMenu.height)
        except:
            y = 40
        x = 0
            
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(ConfigInfoPanel(self))
    
class ConfigInfoPanel(guibase.BasePanel):
    """Panel for User Config information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 1
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(8, cells))
        
        # subject title
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (0, 0, 1, 3))
        self.lblTitle = pyui.widgets.Label(text='', type=1)
        self.addChild(self.lblTitle, (1, 1, 3, 1))
        self.btnSurrender = pyui.widgets.Button('Surrender Game', self.onSurrender)
        self.addChild(self.btnSurrender, (6, 1, 2, 1))
        
        n = 4
        self.lbl = pyui.widgets.Label(text='CHANGE EMPIRE INFO:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lbl = pyui.widgets.Label(text='Email Address:', type=2)
        self.addChild(self.lbl, (0, n+1, 2, 1))
        self.txtEmail = pyui.widgets.Edit('',50)
        self.addChild(self.txtEmail, (2, n+1, 4, 1))
        self.btnEmail = pyui.widgets.Button('Change Email', self.onChangeEmail)
        self.addChild(self.btnEmail, (6, n+1, 2, 1))
        self.lbl = pyui.widgets.Label(text='Login Password:', type=2)
        self.addChild(self.lbl, (0, n+2, 2, 1))
        self.txtPassword = pyui.widgets.Edit('',20)
        self.addChild(self.txtPassword, (2, n+2, 2, 1))
        self.btnEmail = pyui.widgets.Button('Change Password', self.onChangePassword)
        self.addChild(self.btnEmail, (6, n+2, 2, 1))
        
        # starship captains
        n = n+4
        self.lbl = pyui.widgets.Label(text='SELECT STARSHIP CAPTAIN:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstCaptains = pyui.widgets.ListBox(self.onCaptainSelected,None,100,100,0)
        self.addChild(self.lstCaptains, (0, n+1, 8, 16+x))
        
        n = n+18+x
        self.lbl = pyui.widgets.Label(text='Selected Captain Name:', type=2)
        self.addChild(self.lbl, (0, n, 2, 1))
        self.txtName = pyui.widgets.Edit('',20)
        self.addChild(self.txtName, (2, n, 2, 1))
        self.btnName = pyui.widgets.Button('Change Captain Name', self.onChangeName)
        self.addChild(self.btnName, (4, n, 2, 1))
        
        self.pack
        self.populate()
    
    def buildCaptainsData(self):
        """Display all Captains in Empire"""
        d = {}
        # sort captains by experience level
        ##captains = anwp.func.funcs.sortDictByChildObjValue(self.frame.mode.game.myCaptains, 'experience', True, {})
        for captainID, myCaptainDict in self.frame.mode.game.myCaptains.iteritems():
            d[captainID] = '%s - RANK:%s' % (myCaptainDict['name'], myCaptainDict['rank'])
        return d
    
    def onCaptainSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnName.disable()
        else:
            if self.lstCaptains.selected <> -1:
                self.btnName.enable()
                self.txtName.setText(self.frame.mode.game.myCaptains[item.data]['name'])
    
    def onChangeEmail(self, item):
        """Change Email Address"""
        try:
            d = {}
            d['emailAddress'] = self.txtEmail.text
            serverResult = self.frame.mode.game.server.setEmpire(self.frame.mode.game.authKey, d)
            if serverResult == 1:
                self.frame.mode.game.myEmpire['emailAddress'] = self.txtEmail.text
                self.frame.mode.modeMsgBox('Empire Email Address Changed')
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onChangeEmail->Connection to Server Lost, Login Again')
    
    def onSurrender(self, item):
        """Surrender Game"""
        self.frame.mode.modeYesNoBox('Do you really want to surrender the game?', 'surrenderYes', 'surrenderNo')
                    
    def onChangeName(self, item):
        """Change Selected Captain Name"""
        try:
            id = self.lstCaptains.getSelectedItem().data
            serverResult = self.frame.mode.game.server.setCaptainName(self.frame.mode.game.authKey, id, self.txtName.text)
            if serverResult == 1:
                self.frame.mode.game.myCaptains[id]['name'] = self.txtName.text
                self.frame.mode.modeMsgBox('Captain name Changed')
                self.populate()
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onChangeName->Connection to Server Lost, Login Again')
    
    def onChangePassword(self, item):
        """Change Password"""
        try:
            d = {}
            d['password'] = self.txtPassword.text
            serverResult = self.frame.mode.game.server.setEmpire(self.frame.mode.game.authKey, d)
            if serverResult == 1:
                self.frame.mode.game.empirePass = self.txtPassword.text
                self.frame.mode.modeMsgBox('Empire Password Changed')
            else:
                self.frame.mode.modeMsgBox(serverResult)
        except:
            self.frame.mode.modeMsgBox('onChangePassword->Connection to Server Lost, Login Again')
    
    def populate(self):
        """Populate frame with new data"""
        self.btnName.disable()
        
        try:
            myEmpireDict = self.frame.mode.game.myEmpire
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, myEmpireDict['imageFile'])
            self.lblTitle.setText('CONFIGURATION FOR: %s' % myEmpireDict['name'])
            self.lblTitle.setColor(anwp.func.globals.colors[myEmpireDict['color1']])
            myCaptains = self.buildCaptainsData()
            self.txtEmail.setText(myEmpireDict['emailAddress'])
            self.txtPassword.setText(self.frame.mode.game.empirePass)
        except:
            # this allows for testing panel outside game
            myEmpirePict = self.testImagePath + 'empire1.png'
            self.lblTitle.setText('CONFIGURATION FOR: Test')
            myCaptains = self.testDict
        
        self.pctEmpire.setFilename(myEmpirePict)
        self.populateListbox(self.lstCaptains, myCaptains)
            
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Config Info Panel')
    app = run.TestApplication(width, height)
    frame = ConfigInfoFrame(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
