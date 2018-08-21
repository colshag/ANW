# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# notebookControl.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the parent Notebook Control used in ANW Admin
# ---------------------------------------------------------------------------
import sys
import wx

import gridControl

class NotebookControl(wx.Notebook):
    def __init__(self, parent, id, log):
        wx.Notebook.__init__(self, parent, id, size=(21,21),
                             style= wx.NB_MULTILINE
                             #wx.NB_TOP # | wx.NB_MULTILINE
                             #wx.NB_BOTTOM
                             #wx.NB_LEFT
                             #wx.NB_RIGHT
                             )
        self.log = log
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def MakeTabs(self, *args):
        """Recieve tuples of data, each one contains:
        - grid name, aw object, spaces required
        Generate Grid object place in tab within notebook control"""
        for t in args:
            name = t[0]
            gridObjectName = name + 'Grid'
            obj = t[1]
            spaces = t[2]
            self.__dict__[gridObjectName] = self.MakeGrid(obj, spaces)
            newGridObject = getattr(self, gridObjectName)
            self.AddPage(newGridObject, name)

    def MakeGrid(self, obj, spaces = 4):
        """Create a Grid depending on what default obj is given"""
        win = gridControl.GridControl(self, self.log, obj, spaces)
        return win

    def ClearGrids(self):
        """Clear all Grids of data"""
        pass

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "demo Notebook Control Test", size=(1024,768))
        self.notebook = NotebookControl(self, -1, log)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

