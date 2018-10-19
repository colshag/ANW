# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# miscrollvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to create a number
# number is saved to mode, number can be negative
# ---------------------------------------------------------------------------
from anw.gui import scrollvalue

class MIScrollValue(scrollvalue.ScrollValue):
    """The Scroll Value Gui"""
    def __init__(self, path, x, y, name, addMarines, myParent):
        self.addMarines = addMarines
        self.myParent = myParent
        scrollvalue.ScrollValue.__init__(self, path, x, y, name, 'Z')

    def createTitleCard(self, name, text, wordwrap, x, z, scale=0.025):
        """Default Title label for gui controls"""
        if self.addMarines == 1:
            text = 'Choose Amount of Selected Regiment to Add:'
        else:
            text = 'Choose Amount of Regiment order to Reduce:'
        scrollvalue.ScrollValue.createTitleCard(self, name, text, wordwrap, x, z, scale=0.025)
        
    def pressS(self):
        """Submit value to server"""
        if self.addMarines == 1:
            self.mode.addRegimentOrder(self.currentValue, self.id, self.myParent.mySystemDict['id'])
        else:
            self.mode.modifyRegimentOrder(self.currentValue, self.id)
        self.disableButton('S')
    
if __name__ == "__main__":
    myScrollValue = MIScrollValue('media', -0.3, -0.17, 'scroll', addMarines=0, myParent=None)
    myScrollValue.setMaxValue(219)
    myScrollValue.setMinValue(-119)
    run()