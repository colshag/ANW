# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# footer.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a gui panel it contains game specific information
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals

class Footer(guibase.BaseWindow):
    """The Footer contains Empire specific information"""
    def __init__(self, mode, app):
        self.width = app.width
        self.height = 20
        x = 0
        y = app.height - 20
        guibase.BaseWindow.__init__(self, mode, x, y, self.width, self.height)
        self.setPanel(FooterPanel(self))

class FooterPanel(pyui.base.Panel):
    """The Footer Panel contains:
       Empire Name, Round, CR, AL, EC, IA, End Time"""
    def __init__(self, window):
        self.window = window
        self.empireInfo = window.mode.game.myEmpire
        self.galaxyInfo = window.mode.game.myGalaxy
        pyui.widgets.Panel.__init__(self)
        self.setLayout(pyui.layouts.TableLayoutManager(9, 1))
        
        # create widgets
        try:
            self.lblEmpireName = pyui.widgets.Label(text='Empire: %s' % self.empireInfo['name'], color=anwp.func.globals.colors[self.empireInfo['color1']])
        except:
            self.lblEmpireName = pyui.widgets.Label(text='Empire: %s' % self.empireInfo['name'], color=anwp.func.globals.colors['red'])
        self.lblRound = pyui.widgets.Label(text='Round: %s' % self.galaxyInfo['currentRound'], type=2)
        self.lblCR = pyui.widgets.Label(text='CR:%d' % int(self.empireInfo['CR']), type=1)
        self.lblCR.setColor(anwp.func.globals.colors['green'])
        self.lblAL = pyui.widgets.Label(text='AL:%d' % int(self.empireInfo['AL']), type=1)
        self.lblAL.setColor(anwp.func.globals.colors['blue'])
        self.lblEC = pyui.widgets.Label(text='EC:%d' % int(self.empireInfo['EC']), type=1)
        self.lblEC.setColor(anwp.func.globals.colors['yellow'])
        self.lblIA = pyui.widgets.Label(text='IA:%d' % int(self.empireInfo['IA']), type=1)
        self.lblIA.setColor(anwp.func.globals.colors['red'])
        if self.galaxyInfo['currentHoursLeft'] == 1:
            label = 'ROUND FORCED IN 1 HOUR!'
        else:
            label = 'Round Forced in: %s Hours' % self.galaxyInfo['currentHoursLeft']
        self.lblEndDate = pyui.widgets.Label(text=label, type=2)
        
        # place widgets
        self.addChild(self.lblEmpireName, (0, 0, 2, 1))
        self.addChild(self.lblRound, (2, 0, 1, 1))
        self.addChild(self.lblCR, (3, 0, 1, 1))
        self.addChild(self.lblAL, (4, 0, 1, 1))
        self.addChild(self.lblEC, (5, 0, 1, 1))
        self.addChild(self.lblIA, (6, 0, 1, 1))
        self.addChild(self.lblEndDate, (7, 0, 2, 1))
        
        self.pack
    
    def populate(self):
        """Populate Panel with new values"""
        self.lblCR.setText('CR:%d' % int(self.empireInfo['CR']))
        self.lblAL.setText('AL:%d' % int(self.empireInfo['AL']))
        self.lblEC.setText('EC:%d' % int(self.empireInfo['EC']))
        self.lblIA.setText('IA:%d' % int(self.empireInfo['IA']))

def main():
    """Run gui for testing"""
    import anwp.gui.run
    import anwp.client.game
    import anwp.modes.mode
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Footer Panel')
    app = anwp.gui.run.TestApplication(width, height)
    game = anwp.client.game.TestGame(app, width, height)
    mode = anwp.modes.mode.TestMode(game)
    window = Footer(mode, app)
    app.addGui(window)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()