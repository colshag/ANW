# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sendmailbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to send mail to another user through the game
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class SendMailButton(RootButton):
    """The Send Mail Button"""
    def __init__(self, path, x=0.35, y=-0.58):
        RootButton.__init__(self, path, x=x, y=y, name='diplomacy')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['sendmail']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presssendmail(self):
        """Send Mail to other Empire"""
        self.mode.sendMail()
    
if __name__ == "__main__":
    myMenu = SendMailButton('media')
    run()