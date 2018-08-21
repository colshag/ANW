# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# battlemenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Contains the battle mode sub menu
# ---------------------------------------------------------------------------
import pyui
import msgbox
import mainmenu

class MainMenuBattle(mainmenu.MainMenu):
    """Extention of Main Menu for Battle Mode"""  
    def __init__(self, mode, app):
        mainmenu.MainMenu.__init__(self, mode, app)
        self.setPanel(MainMenuBattlePanel(self))

class MainMenuBattlePanel(mainmenu.MainMenuPanel):
    """Sub Menu Panel"""
    def __init__(self, frame):
        mainmenu.MainMenuPanel.__init__(self, frame)
        
        # disable map button
        self.btnBattles.disable()
        
        # create more widgets
        self.btnSimBattle = pyui.widgets.Button('Simulate a Ship Battle', self.onButton)
        self.btnPastBattle = pyui.widgets.Button('View Past Ship Battles', self.onButton)
        
        # place widgets in Frame
        self.addChild(self.btnSimBattle, (0, 1, 3, 1))
        self.addChild(self.btnPastBattle, (3, 1, 3, 1))
        self.pack

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing MainMenuBattle Panel')
    app = run.TestApplication(width, height)
    frame = MainMenuBattle(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()