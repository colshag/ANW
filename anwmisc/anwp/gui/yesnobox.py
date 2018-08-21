# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# yesnobox.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a standard yes/no message box
# ---------------------------------------------------------------------------
import pyui
import guibase

class YesNoBox(guibase.BaseFrame):
    """A YesNoBox is a Frame that displays a message to the User, with a yes/no question
    message and onYes/onNo are string descriptions of owner mode method to run"""
    def __init__(self, mode, app, title, text, onYes, onNo):
        self.width = 1000 # 3 * 200 across
        self.height = 90 # 3 * 30 down
        self.onYes = onYes
        self.onNo = onNo
        x = (app.width - self.width) / 2
        y = (app.height - self.height) / 2
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(YesNoBoxPanel(self, text))
    
class YesNoBoxPanel(pyui.widgets.Panel):
    """Panel that contains:
    message text label
    Yes, No Buttons"""
    def __init__(self, frame, text):
        self.frame = frame
        pyui.widgets.Panel.__init__(self)
        self.setLayout(pyui.layouts.TableLayoutManager(2, 3))

        # create widgets
        self.txtLabel = pyui.widgets.Label(text=text, type=1)
        self.addChild(self.txtLabel, (0, 1, 2, 1))
        self.btnYes = pyui.widgets.Button('Yes', self.onYes)
        self.addChild(self.btnYes, (0, 2, 1, 1))
        self.btnNo = pyui.widgets.Button('No', self.onNo)
        self.addChild(self.btnNo, (1, 2, 1, 1))
        self.pack

    def onYes(self, item):
        """Yes Button Pressed"""
        meth = getattr(self.frame.mode, self.frame.onYes)
        if meth:
            return apply(meth)
        
    def onNo(self, item):
        """No Button Pressed"""
        meth = getattr(self.frame.mode, self.frame.onNo)
        if meth:
            return apply(meth)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0)
    app = run.TestApplication(width, height)
    frame = YesNoBox(None, app, 'Test YesNoBox', 'Test of a YesNo Box','','')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()