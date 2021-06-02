#!/usr/bin/python3

"""
Starting class for the whitebear editor GUI. This class is necessary and must be in all wx python programs.
OnInit must be overridden here.
# TODO fix bugs and package this into a binary.
# TODO spellcheck.
# TODO plaintext editor for styles and robots.
# TODO changing color/bold inside heading without selection allow multicolored headings, same problem inside links.
# TODO https://www.blog.pythonlibrary.org/2019/03/19/distributing-a-wxpython-application/
"""

import wx
import wx.adv

from Constants.Constants import Strings
from Gui.Frames.MainFrame import MainFrame


class WhitebearEditor(wx.App):
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
    app = WhitebearEditor(redirect=False, filename=Strings.editor_output_debug_file)
    app.MainLoop()
