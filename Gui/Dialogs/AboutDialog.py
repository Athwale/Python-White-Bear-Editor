import wx
import wx.html

from Constants.Constants import Strings


class AboutDialog(wx.Dialog):

    def __init__(self, parent):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_about)
        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetMinSize((410, 250))

        self._html_window = wx.html.HtmlWindow(self, style=wx.html.HW_SCROLLBAR_NEVER)
        if 'gtk2' in wx.PlatformInfo:
            self._html_window.SetStandardFonts()

        self._close_button = wx.Button(self, wx.ID_OK, Strings.button_close)
        self._close_button.SetDefault()
        self._html_window.SetPage(Strings.text_about_contents)

        self._main_vertical_sizer.Add(self._html_window, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._close_button, flag=wx.EXPAND)
        self.SetSizer(self._main_vertical_sizer)

        self.ShowModal()
        self.Destroy()
