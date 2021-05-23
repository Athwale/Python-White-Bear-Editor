import wx


class TestFrame(wx.Frame):

    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._main_sizer)

    def dlg_test(self) -> None:
        TestDialog(self)


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
        self.frame.dlg_test()
        return True


class TestDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title='Strings', size=(200, 200))
        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._main_vertical_sizer)

        self.CenterOnParent()

        # Show modal shows centered, show alone does not.
        self.Maximize()
        self.Show()
        self.Maximize(False)


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
