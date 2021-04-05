#!/usr/bin/python3

"""
Starting class for the whitebear editor GUI. This class is necessary and must be in all wx python programs.
OnInit must be overridden here.
# todo deploy as package
"""
import wx
import wx.adv

from Constants.Constants import Strings
from Gui.Frames.MainFrame import MainFrame


class MyApp(wx.App):
    """
    Main class for running the gui.
    """

    def __init__(self, redirect, filename):
        wx.App.__init__(self, redirect, filename)
        self._frame = None

    def OnInit(self):
        # Frame with None parent is a top level frame. This frame must be created after the App object is created.
        self._frame = MainFrame()
        # Optional set the frame as the main one, the main window is the default parent for dialogs without parent set.
        self.SetTopWindow(self._frame)
        self._frame.Show()
        return True

    def OnExit(self):
        print('_Done_')
        return True


if __name__ == "__main__":
    # Redirect allows the gui to show a window with std and err text output, or if set, send it to a file.
    app = MyApp(redirect=False, filename=Strings.editor_output_debug_file)
    app.MainLoop()