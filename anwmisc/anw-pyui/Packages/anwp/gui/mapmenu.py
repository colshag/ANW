# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mapmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Contains the galactic map menu
# ---------------------------------------------------------------------------
import pyui
import msgbox
import mainmenu
import anwp.func.globals

class MainMenuMap(mainmenu.MainMenu):
    """Extention of Main Menu for Map Mode"""  
    def __init__(self, mode, app):
        mainmenu.MainMenu.__init__(self, mode, app)
        self.setPanel(MainMenuMapPanel(self))

class MainMenuMapPanel(mainmenu.MainMenuPanel):
    """Sub Menu Panel"""
    def __init__(self, frame):
        mainmenu.MainMenuPanel.__init__(self, frame)
        
        # disable map button
        self.btnMap.disable()
        
        # create more widgets
        self.btnViewRadar = pyui.widgets.Button('View Radar', self.onButton)
        if 'View Diplomacy' in self.frame.mode.game.myEmpire['help']:
            self.btnViewDiplomacy = pyui.widgets.Button('View Diplomacy', self.onButton, fgColor=anwp.func.globals.colors['yellow'], bgColor=anwp.func.globals.colors['red'])
        else:
            self.btnViewDiplomacy = pyui.widgets.Button('View Diplomacy', self.onButton)
        self.btnViewResources = pyui.widgets.Button('View Resources', self.onButton)
        self.btnViewTradeRoutes = pyui.widgets.Button('View Trade Routes', self.onButton)
        
        # place widgets in Frame
        self.addChild(self.btnViewRadar, (0, 1, 3, 1))
        self.addChild(self.btnViewDiplomacy, (3, 1, 3, 1))
        self.addChild(self.btnViewResources, (6, 1, 3, 1))
        self.addChild(self.btnViewTradeRoutes, (9, 1, 3, 1))
        self.pack

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing MainMenuMap Panel')
    app = run.TestApplication(width, height)
    frame = MainMenuMap(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()