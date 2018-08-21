# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mainmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a gui panel it contains the main menu for the game
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals

class MainMenu(guibase.BaseWindow):
    """The Main Menu contains buttons that allows the user to traverse to the different
       game modes.  It also contains functionality that will color-code buttons to
       get the users attention"""
    def __init__(self, mode, app):
        self.width = app.width # the main menu takes up the entire top of the game screen
        self.height = 60 # 2 * 30 down
        x = 0
        y = 0
        guibase.BaseWindow.__init__(self, mode, x, y, self.width, self.height)
        self.setPanel(MainMenuPanel(self))
        
class MainMenuPanel(guibase.BasePanel):
    """Panel that contains:
    1st Row: Mail, Research, Map, War, Diplomacy, Market, Design, Sim, History, Config, Help, Exit
    2nd Row: Sub Buttons for several of the above modes"""
    def __init__(self, window):
        guibase.BasePanel.__init__(self, window)
        self.setLayout(pyui.layouts.TableLayoutManager(12, 2))
        self.mode = window.mode
        
        # create widgets
        for name in ['Map','Mail','Tech','Battles','Mail','Market','Design',
                     'Config','Status','EndTurn','Help']:
            if name in self.frame.mode.game.myEmpire['help']:
                setattr(self, 'btn%s' % name, pyui.widgets.Button(name, self.onButton, 
                                                              fgColor=anwp.func.globals.colors['yellow'], bgColor=anwp.func.globals.colors['red']))
            else:
                setattr(self, 'btn%s' % name, pyui.widgets.Button(name, self.onButton))
        self.btnExit = pyui.widgets.Button('Exit', self.onExit)
        
        # place widgets in Frame
        self.addChild(self.btnMap, (0, 0, 1, 1))
        self.addChild(self.btnTech, (1, 0, 1, 1))
        self.addChild(self.btnBattles, (2, 0, 1, 1))
        self.addChild(self.btnMail, (3, 0, 1, 1))
        self.addChild(self.btnMarket, (4, 0, 1, 1))
        self.addChild(self.btnDesign, (5, 0, 1, 1))
        self.addChild(self.btnConfig, (6, 0, 1, 1))
        self.addChild(self.btnStatus, (7, 0, 1, 1))
        self.addChild(self.btnEndTurn, (8, 0, 1, 1))
        self.addChild(self.btnHelp, (9, 0, 1, 1))
        self.addChild(self.btnExit, (11, 0, 1, 1))
        self.pack
        
    def onButton(self, item):
        """Enter the Mode specified by the Button"""
        import anwp.modes.modemap
        import anwp.modes.modetech
        import anwp.modes.modemail
        import anwp.modes.modemarket
        import anwp.modes.modedesign
        import anwp.modes.modebattle
        import anwp.modes.modeconfig
        import anwp.modes.modehelp
        
        try:
            game = self.frame.mode.game
        except:
            pass
        newMode = 0
        if item.text == 'Map':
            newMode = anwp.modes.modemap.ModeMap(game)
        elif item.text == 'View Radar':
            self.frame.mode.toggleRadar()
        elif item.text == 'View Resources':
            self.frame.mode.toggleResources()
        elif item.text == 'View Trade Routes':
            self.frame.mode.toggleTradeRoutes()
        elif item.text == 'View Diplomacy':
            self.frame.mode.toggleDiplomacy()   
        elif item.text == 'Mail':
            newMode = anwp.modes.modemail.ModeMail(game)
        elif item.text == 'Tech':
            if self.frame.mode.game.myTech['200']['complete'] == 1:
                newMode = anwp.modes.modetech.ModeTech3(game)
            elif self.frame.mode.game.myTech['100']['complete'] == 1:
                newMode = anwp.modes.modetech.ModeTech2(game)
            else:
                newMode = anwp.modes.modetech.ModeTech1(game)
        elif item.text == '1st Age of Technology':
            newMode = anwp.modes.modetech.ModeTech1(game)
        elif item.text == '2nd Age of Technology':
            newMode = anwp.modes.modetech.ModeTech2(game)
        elif item.text == '3rd Age of Technology':
            newMode = anwp.modes.modetech.ModeTech3(game)
        elif item.text == 'Battles':
            newMode = anwp.modes.modebattle.ModeBattle(game)
        elif item.text == 'Simulate a Ship Battle':
            self.frame.mode.setSimBattle()
        elif item.text == 'View Past Ship Battles':
            self.frame.mode.setPastBattle()
        elif item.text == 'Market':
            newMode = anwp.modes.modemarket.ModeMarket(game)
        elif item.text == 'Design':
            newMode = anwp.modes.modedesign.ModeDesign(game)
        elif item.text == 'Config':
            newMode = anwp.modes.modeconfig.ModeConfig(game)
        elif item.text == 'EndTurn':
            self.frame.mode.checkEndTurn()
        elif item.text == 'Status':
            self.frame.mode.askForHelp()
        elif item.text == 'Help':
            newMode = anwp.modes.modehelp.ModeHelp(game)
        elif '?' in item.text:
            self.frame.mode.setHelp(item.text)
        else:
            print 'MODE', 'MODE: %s, not setup yet...' % item.text
            return
        if newMode <> 0:
            game.enterMode(newMode)
    
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing MainMenu Panel')
    app = run.TestApplication(width, height)
    frame = MainMenu(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    