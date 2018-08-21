# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sendmailinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows player to send mail to other empires
# ---------------------------------------------------------------------------
import types

import pyui
import guibase

class SendMailInfoFrame(guibase.BaseFrame):
    """Displays Mail Information"""  
    def __init__(self, mode, app, empireDict):
        self.app = app
        self.width = 1000
        self.empireDict = empireDict
        self.height = 120 # 4 * 30 down
        x = (app.width - self.width) / 2
        y = (app.height - self.height) / 2
        
        title = 'Send Galactic Mail to: %s' % empireDict['name']
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(SendMailInfoPanel(self))
    
class SendMailInfoPanel(guibase.BasePanel):
    """Panel for all Send Mail information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 4))
        
        n = 0
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (0, n, 1, 3))
        self.lbl = pyui.widgets.Label(text='PLEASE TYPE A MESSAGE BELOW AND CLICK SEND:', type=2)
        self.addChild(self.lbl, (0, n+1, 7, 1))
        self.txtMessage = pyui.widgets.Edit('', 90)
        self.addChild(self.txtMessage, (1, n+2, 7, 1))
        self.btnSendMail = pyui.widgets.Button('Send Message', self.onSendMail)
        self.addChild(self.btnSendMail, (0, n+3, 4, 1))
        self.btnSendMail.enable()
        self.btnCancel = pyui.widgets.Button('Cancel', self.onCancel)
        self.addChild(self.btnCancel, (4, n+3 , 4, 1))
        
        # pack widgets
        self.pack
        
        # populate picture
        try:
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, self.frame.empireDict['imageFile'])
        except:
            myEmpirePict = self.testImagePath + 'empire1.png'
        self.pctEmpire.setFilename(myEmpirePict)
    
    def onSendMail(self, item):
        """Send Mail to Server"""
        self.frame.mode.sendMail(self.frame.empireDict['id'], self.txtMessage.text)
        
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Send Mail Info Panel')
    app = run.TestApplication(width, height)
    empireDict = {'id':'1', 'name':'Test Empire'}
    frame = SendMailInfoFrame(None, app, empireDict)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
