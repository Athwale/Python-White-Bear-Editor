#!/usr/bin/python3

"""Starting class for the whitebear editor GUI. This
class is necessary and must be in all wx python programs. OnInit must be overridden here"""

import time

import wx
import wx.adv

from Constants.Constants import Strings, Numbers
from Gui.Frames.MainFrame import MainFrame
from Resources.Fetch import Fetch


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self, redirect, filename):
        wx.App.__init__(self, redirect, filename)
        self.frame = None

    def OnInit(self):
        # Set up and display ad splash screen
        bitmap = wx.Bitmap(Fetch.get_resource_path('splashscreen.png'), wx.BITMAP_TYPE_PNG)
        wx.adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTER_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                            Numbers.splashscreen_timeout, None, -1,
                            wx.DefaultPosition, wx.DefaultSize, wx.BORDER_SIMPLE)
        wx.Yield()
        # Frame with None parent is a top level frame. This frame must be created after the App object is created.
        self.frame = MainFrame()
        # Optional set the frame as the main one, the main window is the default parent for dialogs without parent set.
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

    def OnExit(self):
        print('_Done_')
        return True


if __name__ == "__main__":
    # Redirect allows the gui to show a window with std and err text output, or if set, send it to a file.
    app = MyApp(redirect=False, filename=Strings.editor_output_debug_file)
    wx.Yield()
    time.sleep((Numbers.splashscreen_timeout / 1000) - 2)
    app.MainLoop()
