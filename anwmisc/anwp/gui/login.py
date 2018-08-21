# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# login.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows a user to select from a list, give a password, and login
# ---------------------------------------------------------------------------
import pyui
import guibase

class LoginFrame(guibase.BaseFrame):
    """Basic Login Frame, requires position, passes data to Panel"""  
    def __init__(self, mode, app, title, dataLable, dataDict, onLoginMethod):
        self.onLoginMethod = onLoginMethod
        self.width = 500 # 2 * 250 across
        self.height = 360 # 12 * 30 down
        x = (app.width - self.width) / 2
        y = (app.height - self.height) / 2
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(LoginPanel(self, dataLable, dataDict))

class LoginPanel(guibase.BasePanel):
    """Panel that contains:
    Label
    Listbox
    password textbox
    Login Button
    Exit Button"""
    def __init__(self, frame, dataLable, dataDict):
        guibase.BasePanel.__init__(self, frame)        
        self.setLayout(pyui.layouts.TableLayoutManager(2, 12))
        
        if self.frame.onLoginMethod <> 'loginToServer':
            # create Labels
            self.lblData = pyui.widgets.Label(text=dataLable, type=2)
            self.addChild(self.lblData,  (0, 1, 2, 1))
            self.lblPass = pyui.widgets.Label(text='Enter Password:', type=1)
            self.addChild(self.lblPass,  (0, 2, 1, 1))
        
            # create Password Textbox
            self.txtPass = pyui.widgets.Password('', 18, None)
            self.addChild(self.txtPass,  (1, 2, 1, 1))
        
        # create Listbox
        self.lstData = pyui.widgets.ListBox(self.onSelected, None)
        self.populateListbox(self.lstData, dataDict)
        self.addChild(self.lstData,  (0, 3, 2, 7))
        
        # create Buttons
        self.btnLogin = pyui.widgets.Button('Login', self.onLogin)
        self.addChild(self.btnLogin, (0, 11, 1, 1))
        self.btnLogin.disable()
        self.btnExit = pyui.widgets.Button('Exit', self.onExit)
        self.addChild(self.btnExit,  (1, 11, 1, 1))
        self.pack
    
    def onLogin(self, item):
        """Do the specified login code with listdata and textdata"""
        if self.frame.onLoginMethod == 'createEmpireLogin':
            self.frame.mode.createEmpireLogin(self.selectedItemName, self.txtPass.text)
        elif self.frame.onLoginMethod == 'loginToGame':
            self.frame.mode.loginToGame(self.selectedItemData, self.txtPass.text)
        elif self.frame.onLoginMethod == 'loginToServer':
            self.frame.mode.loginToServer(self.selectedItemData)

    def onSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnLogin.disable()
        else:
            self.selectedItemName = item.name
            self.selectedItemData = item.data
            self.btnLogin.enable()

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    dataDict = {'2':'Empire2', '1':'Empire1', '3':'Empire3'}
    pyui.init(width, height, 'p3d', 0, 'Testing Login Panel')
    app = run.TestApplication(width, height)
    frame = LoginFrame(None, app, 'Please Choose a Something:', 'http://lewis.dnsalias.com/:8000', dataDict, 'TestMethod')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
