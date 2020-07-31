import wx
import wx.html

from Constants.Strings import Strings


class AboutDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_about)
        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetMinSize((410, 250))

        self.html_window = wx.html.HtmlWindow(self, style=wx.html.HW_SCROLLBAR_NEVER)
        if 'gtk2' in wx.PlatformInfo:
            self.html_window.SetStandardFonts()

        self.close_button = wx.Button(self, wx.ID_OK, Strings.button_close)
        self.close_button.SetDefault()
        self.html_window.SetPage(Strings.text_about_contents)

        self.main_vertical_sizer.Add(self.html_window, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.close_button, flag=wx.EXPAND)
        self.SetSizer(self.main_vertical_sizer)

        self.ShowModal()
        self.Destroy()
