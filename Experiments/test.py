import wx


class TestFrame(wx.Frame):

    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._main_sizer)


class MyApp(wx.App):
    """
    Main class for running the gui.
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = TestFrame(None, -1, "Test", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
