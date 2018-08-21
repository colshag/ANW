# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# simmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a gui panel it contains the simulator menu for the game
# ---------------------------------------------------------------------------
import pyui
import guibase

class SimMenu(guibase.BaseWindow):
    """The Sim Menu contains buttons to allow functionality within the Battle Simulator"""
    def __init__(self, mode, app):
        self.width = 300 # Change this as required
        self.height = 30 # 1 * 30 down
        x = 0
        y = 0
        guibase.BaseWindow.__init__(self, mode, x, y, self.width, self.height)
        self.setPanel(SimMenuPanel(self))
        
class SimMenuPanel(guibase.BasePanel):
    """Panel that contains:
    1st Row: Exit, Pause/Resume"""
    def __init__(self, window):
        guibase.BasePanel.__init__(self, window)
        self.setLayout(pyui.layouts.TableLayoutManager(2, 1))
        self.mode = window.mode
        
        # create widgets
        self.btnPause = pyui.widgets.Button('Pause/Resume', self.onButton)
        if self.frame.mode.toLogin == True:
            self.btnExit = pyui.widgets.Button('Login to Game', self.onButton)
        else:
            self.btnExit = pyui.widgets.Button('Exit Replay', self.onButton)
        
        # place widgets in Frame
        self.addChild(self.btnExit, (0, 0, 1, 1))
        self.addChild(self.btnPause, (1, 0, 1, 1))
        self.pack
        
    def onButton(self, item):
        """Each button has their own code"""
        try:
            import anwp.modes.modelogin
            game = self.frame.mode.game
        except:
            pass
        newMode = 0
        if item.text == 'Login to Game':
            newMode = anwp.modes.modelogin.ModeLogin(game)
        elif item.text == 'Exit Replay':
            newMode = anwp.modes.modebattle.ModeBattle(game)
        elif item.text == 'Pause/Resume':
            self.frame.mode.pauseResume()
        else:
            print 'MODE', 'MODE: %s, not setup yet...' % item.text
            return
        if newMode <> 0:
            game.enterMode(newMode)
    
def main():
    """Run gui for testing"""
    import run
    width = 1280
    height = 1024
    pyui.init(width, height, 'p3d', 0, 'Testing SimMenu Panel')
    app = run.TestApplication(width, height)
    frame = SimMenu(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    