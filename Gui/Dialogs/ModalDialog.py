import wx


class ModalDialog(wx.Dialog):

    def __init__(self, parent, title, contents):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        :param title: Title of the window
        :param contents: Contents of the window.
        """
        # TODO Add close button
        wx.Dialog.__init__(self, parent, title=title)
        self.main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.text = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        self.text.SetValue(contents)
        self.text.SetBackgroundColour(self.GetBackgroundColour())

        self.main_horizontal_sizer.Add(self.text, 1, flag=wx.EXPAND)
        self.SetSizer(self.main_horizontal_sizer)
        self.SetAutoLayout(1)

        self.ShowModal()
        self.Destroy()

