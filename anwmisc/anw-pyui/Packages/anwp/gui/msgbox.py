# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# msgbox.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a standard message box
# ---------------------------------------------------------------------------
import pyui
import guibase

class MessageBox(guibase.BaseFrame):
    """A MessageBox is a Frame that displays a message to the User"""
    def __init__(self, mode, app, title, text):
        self.width = 1000 # 3 * 200 across
        self.height = 90 # 3 * 30 down
        x = (app.width - self.width) / 2
        y = (app.height - self.height) / 2
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(MessageBoxPanel(self, text))
    
class MessageBoxPanel(pyui.widgets.Panel):
    """Panel that contains:
    message text label
    Ok Button"""
    def __init__(self, frame, text):
        self.frame = frame
        pyui.widgets.Panel.__init__(self)
        self.setLayout(pyui.layouts.TableLayoutManager(3, 3))

        # create widgets
        self.txtLabel = pyui.widgets.Label(text=text, type=1)
        self.btnOk = pyui.widgets.Button('Ok', self.onOk)
        
        # place widgets in Frame
        self.addChild(self.txtLabel, (0, 1, 3, 1))
        self.addChild(self.btnOk, (1, 2, 1, 1))
        self.pack

    def onOk(self, item):
        """Ok Button Pressed, close"""
        self.frame.close()

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0)
    app = run.TestApplication(width, height)
    frame = MessageBox(None, app, 'Test MessageBox', 'Test of a Message Box')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()