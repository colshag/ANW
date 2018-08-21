# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# viewtrade.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel shows current trade route info
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.funcs

class ViewTrade(guibase.BaseWindow):
    """Basic View Trade Window, requires position, passes data to Panel"""
    def __init__(self, mode, app, x, y, myTradeDict):
        self.app = app
        self.width = 250
        self.height = 60 # 2 * 30 down
        self.myTradeDict = myTradeDict
        guibase.BaseWindow.__init__(self, mode, x, y, self.width, self.height)
        self.setPanel(ViewTradePanel(self))

class ViewTradePanel(guibase.BasePanel):
    """Panel that contains:
    Trade info (resources)
    """
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)        
        self.setLayout(pyui.layouts.TableLayoutManager(3, 2))
        
        # trade resource info
        self.pctAL = pyui.widgets.Picture(self.symbolAL)
        self.pctEC = pyui.widgets.Picture(self.symbolEC)
        self.pctIA = pyui.widgets.Picture(self.symbolIA)
        self.addChild(self.pctAL, (0, 0, 1, 1))
        self.addChild(self.pctEC, (1, 0, 1, 1))
        self.addChild(self.pctIA, (2, 0, 1, 1))
        self.lblTotalAL = pyui.widgets.Label(str(self.frame.myTradeDict['AL']), type=1)
        self.lblTotalEC = pyui.widgets.Label(str(self.frame.myTradeDict['EC']), type=1)
        self.lblTotalIA = pyui.widgets.Label(str(self.frame.myTradeDict['IA']), type=1)
        self.addChild(self.lblTotalAL, (0, 1, 1, 1))
        self.addChild(self.lblTotalEC, (1, 1, 1, 1))
        self.addChild(self.lblTotalIA, (2, 1, 1, 1))        

        self.pack
                
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    dTrade = {'AL':100.0, 'EC':100.0, 'IA':100.0}
    pyui.init(width, height, 'p3d', 0, 'Testing Trade Panel')
    app = run.TestApplication(width, height)
    frame = ViewTrade(None, app, 100, 100, dTrade)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
