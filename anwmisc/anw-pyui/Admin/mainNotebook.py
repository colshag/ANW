# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mainNotebook.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main Notebook Control used in ANW Admin
# ---------------------------------------------------------------------------
import sys
import wx

import notebookControl

class MainNotebook(notebookControl.NotebookControl):
    def __init__(self, parent, id, log):
        notebookControl.NotebookControl.__init__(self, parent, id, log)
        
        self.galaxyNotebook = None
        self.empireNotebook = None
        self.shipNotebook = None
        self.regimentNotebook = None
        self.systemNotebook = None
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    def clearNotebooks(self):
        """Clean up notebooks"""
        try:
            self.DeleteAllPages()
        except:
            pass

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "test", size=(1024,768))
        self.notebook = MainNotebook(self, -1, log)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

