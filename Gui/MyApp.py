#!/usr/bin/python3

"""Starting class for the whitebear editor GUI"""

import wx

from Constants.Strings import Strings
from Gui.Frames.MainFrame import MainFrame


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = MainFrame(None, Strings.editor_name)
        self.frame.Show()
        # Optional set the frame as the main one
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
