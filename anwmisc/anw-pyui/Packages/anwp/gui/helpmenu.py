# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# helpmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Contains the help mode sub menu
# ---------------------------------------------------------------------------
import pyui
import msgbox
import mainmenu

class HelpMenu(mainmenu.MainMenu):
    """Extention of Main Menu for Help Mode"""  
    def __init__(self, mode, app):
        mainmenu.MainMenu.__init__(self, mode, app)
        self.height = 90 # 3 * 30 down
        self.setPanel(HelpMenuPanel(self))

class HelpMenuPanel(mainmenu.MainMenuPanel):
    """Sub Menu Panel"""
    def __init__(self, frame):
        mainmenu.MainMenuPanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(12, 3))
        
        # disable help button
        self.btnHelp.disable()
        
        # create widgets
        self.btnHelpGame = pyui.widgets.Button('Game?', self.onButton)
        self.btnHelpEconomy = pyui.widgets.Button('Economy?', self.onButton)
        self.btnHelpTech = pyui.widgets.Button('Tech?', self.onButton)
        self.btnHelpBattles = pyui.widgets.Button('Battles?', self.onButton)
        self.btnHelpDiplomacy = pyui.widgets.Button('Diplomacy?', self.onButton)
        self.btnHelpMarket = pyui.widgets.Button('Market?', self.onButton)
        self.btnHelpDesign = pyui.widgets.Button('Design?', self.onButton)
        self.btnHelpFleets = pyui.widgets.Button('Fleets?', self.onButton)
        self.btnHelpArmies = pyui.widgets.Button('Armies?', self.onButton)
        self.btnHelpEndTurn = pyui.widgets.Button('Turn?', self.onButton)
        self.btnHelpRadar = pyui.widgets.Button('Radar?', self.onButton)
        self.btnHelpData = pyui.widgets.Button('Data?', self.onButton)
        
        # place widgets in Frame
        self.addChild(self.btnHelpGame, (0, 1, 1, 1))
        self.addChild(self.btnHelpEconomy, (1, 1, 2, 1))
        self.addChild(self.btnHelpTech, (3, 1, 1, 1))
        self.addChild(self.btnHelpBattles, (4, 1, 1, 1))
        self.addChild(self.btnHelpDiplomacy, (5, 1, 2, 1))
        self.addChild(self.btnHelpMarket, (7, 1, 1, 1))
        self.addChild(self.btnHelpDesign, (8, 1, 1, 1))
        self.addChild(self.btnHelpFleets, (9, 1, 1, 1))
        self.addChild(self.btnHelpArmies, (10, 1, 1, 1))
        self.addChild(self.btnHelpEndTurn, (11, 1, 1, 1))
        self.addChild(self.btnHelpRadar, (0, 2, 1, 1))
        self.addChild(self.btnHelpData, (1, 2, 1, 1))
        self.pack

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing HelpMenuPanel')
    app = run.TestApplication(width, height)
    frame = HelpMenu(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()