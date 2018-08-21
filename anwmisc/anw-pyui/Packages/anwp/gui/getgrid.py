# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# setfleet.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel returns a grid number for fleet placement
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals

class GetGridFrame(guibase.BaseInfoFrame):
    """Basic Get Grid Frame"""  
    def __init__(self, mode, app, gridNum, maxNum, title, activeGrids):
        guibase.BaseInfoFrame.__init__(self, mode, app, title, 2)
        self.maxNum = maxNum
        self.height = self.width
        self.activeGrids = activeGrids
        self.setPanel(GetGridPanel(self, gridNum))

class GetGridPanel(guibase.BasePanel):
    """Get Grid Panel"""
    def __init__(self, frame, gridNum):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(gridNum, gridNum))
        
        num1 = self.frame.maxNum
        num2 = 1
        for y in range(gridNum):
            for x in range(gridNum):
                # create buttons 1-maxNum+gridNum
                num = num1+num2
                if num in self.frame.activeGrids:
                    setattr(self, 'btn%d' % num, pyui.widgets.Button(str(num), self.onButton, fgColor=anwp.func.globals.colors['yellow'], bgColor=anwp.func.globals.colors['red']))
                else:
                    setattr(self, 'btn%d' % num, pyui.widgets.Button(str(num), self.onButton))
                myButton = getattr(self, 'btn%d' % num)
                self.addChild(myButton, (x, y, 1, 1))
                num2 += 1
            num1 -= gridNum
            num2 = 1
        
        self.pack
    
    def onButton(self, item):
        """Send Chosen Grid Postion back to mode"""
        try:
            self.frame.mode.setFleetGrid(item.text)
        except:
            print item.text

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Grid Panel')
    app = run.TestApplication(width, height)
    ##frame = GetGridFrame(None, app, 5, 20, 'Select Grid Quadrant for Fleet')
    frame = GetGridFrame(None, app, 3, 6, 'Select Map Quadrant for Fleet')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
