import wx


class ModalDialog(wx.Dialog):

    def __init__(self, parent, title, contents):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        :param title: Title of the window
        :param contents: Contents of the window.
        """
        wx.Dialog.__init__(self, parent, title=title)
        text = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.SUNKEN_BORDER | wx.TE_AUTO_URL)
        text.SetValue(contents)
        text.SetBackgroundColour(self.GetBackgroundColour())
        self.ShowModal()
        self.Destroy()
