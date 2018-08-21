# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# techmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Contains the tech mode main menu
# ---------------------------------------------------------------------------
import pyui
import msgbox
import mainmenu

class MainMenuTech(mainmenu.MainMenu):
    """Extention of Main Menu for Tech Mode"""  
    def __init__(self, mode, app):
        mainmenu.MainMenu.__init__(self, mode, app)
        self.setPanel(MainMenuTechPanel(self))

class MainMenuTechPanel(mainmenu.MainMenuPanel):
    """Panel that contains:
    1st Row: Mail, Research, Map, War, Diplomacy, Market, Design, Sim, History, Config, Help, Exit
    2nd Row: 1st Age of Technology, 2nd Age of Technology, 3rd Age of Technology"""
    def __init__(self, frame):
        mainmenu.MainMenuPanel.__init__(self, frame)
        
        # create more widgets
        self.btnTech1 = pyui.widgets.Button('1st Age of Technology', self.onButton)
        self.btnTech2 = pyui.widgets.Button('2nd Age of Technology', self.onButton)        
        self.btnTech3 = pyui.widgets.Button('3rd Age of Technology', self.onButton)
        
        # place widgets in Frame
        self.addChild(self.btnTech1, (0, 1, 4, 1))
        self.addChild(self.btnTech2, (4, 1, 4, 1))
        self.addChild(self.btnTech3, (8, 1, 4, 1))
        self.pack
        
        # disable Research button
        self.btnTech.disable()
    
    def disableButtons(self):
        """Disable Buttons that represent Tech Age"""
        buttonTech = getattr(self, 'btnTech%d' % self.frame.mode.techAge)
        buttonTech.disable()
    
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing MainMenuTech Panel')
    app = run.TestApplication(width, height)
    frame = MainMenuTech(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()