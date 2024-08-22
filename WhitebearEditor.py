#!/usr/bin/python3

"""
Starting class for the whitebear editor GUI. This class is necessary and must be in all wx python programs.
OnInit must be overridden here.
# TODO fix bugs and package this into a binary. Package into rpm.
# TODO https://www.blog.pythonlibrary.org/2019/03/19/distributing-a-wxpython-application/
# TODO https://discuss.wxpython.org/t/cropping-an-image-with-wxpython/34983/6 for logos?

# TODO richtext control does not yet support red waved underline, change underline once available.
# TODO look at cookies from whitebear using requests headers, beware of redirect, set cookie warning if we use them?
# TODO settings from spellcheck dialog do not open
# TODO side panel stretched with less images.
# TODO add files to selectable item in inserting url.
# TODO copy paste with link does not work.
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
