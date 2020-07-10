import wx

from Constants.Strings import Strings
from Gui.Frames.MainFrame import MainFrame


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def OnInit(self):
        frame = MainFrame(None, Strings.editor_name)
        frame.Show()
        return True


app = MyApp()
app.MainLoop()
