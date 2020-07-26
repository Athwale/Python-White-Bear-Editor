import wx
from Constants.Strings import Strings


class AboutDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_about_window_name)
        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        self.close_button = wx.Button(self, wx.ID_OK, Strings.button_close)
        self.close_button.SetDefault()
        self.text.SetValue(Strings.text_about_contents)
        self.text.SetBackgroundColour(self.GetBackgroundColour())

        self.main_vertical_sizer.Add(self.text, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.close_button, flag=wx.EXPAND)
        self.SetSizer(self.main_vertical_sizer)

        self.ShowModal()
        self.Destroy()
