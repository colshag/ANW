# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weapondirection.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to declare weapon direction on ship
# ---------------------------------------------------------------------------
from anw.gui import rootbutton

class WeaponDirection(rootbutton.RootButton):
    """Allows user to declare weapon direction on ship"""
    def __init__(self, path, x, y):
        rootbutton.RootButton.__init__(self, path, x=x, y=y, name='design')
        self.allKeys = ['1','2','3','4']
        self.disableButtonTime = -1
        self.disableButtonIgnore = []
        self.direction = 0
        self.createTitleCard('weapdirection','Weapon Direction:',
                             30,self.posInitX-0.04,self.posInitY+0.07)
        self.press1()
    
    def createButtons(self):
        """Create all Buttons"""
        for key in ['1','2','3','4']:
            buttonPosition = ((self.posInitX+self.x*.10),0,(self.posInitY+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
        self.x = 0
    
    def press1(self):
        """Press Fore Quad"""
        self.enableLastButton('1')
        self.disableButton('1')
        self.direction = 0
    
    def press2(self):
        """Press Aft Quad"""
        self.enableLastButton('2')
        self.disableButton('2')
        self.direction = 180
    
    def press3(self):
        """Press Port Quad"""
        self.enableLastButton('3')
        self.disableButton('3')
        self.direction = 270
    
    def press4(self):
        """Press Star Quad"""
        self.enableLastButton('4')
        self.disableButton('4')
        self.direction = 90

if __name__ == "__main__":
    myGui = WeaponDirection('media', 0, 0)
    run()