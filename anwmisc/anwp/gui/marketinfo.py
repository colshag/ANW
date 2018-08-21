# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# marketinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all galactic market based information
# ---------------------------------------------------------------------------
import pyui
import guibase

class MarketInfoFrame(guibase.BaseFrame):
    """Displays Market Information"""  
    def __init__(self, mode, app, title='Galactic Market Statistics'):
        self.app = app
        self.width = 1024
        try:
            self.height = (app.height - mode.mainMenu.height - mode.mainFooter.height - 40)
        except:
            self.height = (app.height - 120)
        try:
            y = (mode.mainMenu.height)
        except:
            y = 40
        x = 0
            
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(MarketInfoPanel(self))
    
class MarketInfoPanel(guibase.BasePanel):
    """Panel for all Market information"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 11))
        
        # subject title
        self.lblTitle = pyui.widgets.Label(text='CURRENT GALACTIC MARKET STATS:', type=1)
        self.addChild(self.lblTitle, (0, 0, 8, 1))
        self.shtMarket = pyui.sheet.Sheet()
        self.shtMarket.setColumnTitle(1, 'Average Sold AL')
        self.shtMarket.setColumnTitle(2, 'Average Sold EC')
        self.shtMarket.setColumnTitle(3, 'Average Sold IA')
        self.shtMarket.setColumnTitle(4, 'Total Volume AL')
        self.shtMarket.setColumnTitle(5, 'Total Volume EC')
        self.shtMarket.setColumnTitle(6, 'Total Volume IA')
        # setup sheet
        for i in range(1,7):
            self.shtMarket.setColumnWidth(i, 160)
            self.shtMarket.setColumnReadOnly(i)
        
        # put in values
        try:
            for round in range(1,self.frame.mode.game.currentRound):
                myMarketStat = self.frame.mode.game.marketStats[str(round)]
                self.shtMarket.setCellValue(1, round, myMarketStat['avgSoldAL'])
                self.shtMarket.setCellValue(2, round, myMarketStat['avgSoldEC'])
                self.shtMarket.setCellValue(3, round, myMarketStat['avgSoldIA'])
                self.shtMarket.setCellValue(4, round, myMarketStat['volSoldAL'])
                self.shtMarket.setCellValue(5, round, myMarketStat['volSoldEC'])
                self.shtMarket.setCellValue(6, round, myMarketStat['volSoldIA'])
        except:
            pass
                
        self.addChild(self.shtMarket, (0, 1, 8, 10))
        self.pack
            
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Market Info Panel')
    app = run.TestApplication(width, height)
    frame = MarketInfoFrame(None, app)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
