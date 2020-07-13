#!/usr/bin/python3

"""Starting class for the whitebear editor GUI. This
class is necessary and must be in all wx python programs. OnInit must be overridden here"""

import wx

from Constants.Strings import Strings
from Gui.Frames.MainFrame import MainFrame


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self, redirect, filename):
        wx.App.__init__(self, redirect, filename)
        self.frame = None

    def OnInit(self):
        # Frame with None parent is a top level frame. This frame must be created after the App object is created.
        self.frame = MainFrame()
        self.frame.Show()
        # Optional set the frame as the main one, the main window is the default parent for dialogs without parent set.
        self.SetTopWindow(self.frame)
        return True

    def OnExit(self):
        print('Done')
        return True


if __name__ == "__main__":
    # Redirect allows the gui to show a window with std and err text output, or if set, send it to a file.
    app = MyApp(redirect=False, filename=Strings.editor_output_debug_file)
    app.MainLoop()
