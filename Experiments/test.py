import wx
import wx.richtext as rt


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._main_sizer)

        self._bold_button = wx.Button(self, -1, 'bold')
        self._controls_sizer.Add(self._bold_button)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self._main_sizer.Add(self._controls_sizer)

        self.Bind(wx.EVT_BUTTON, self._change_bold, self._bold_button)

        self.rtc.Bind(wx.EVT_KEY_UP, self._handler)
        self.rtc.AppendText('Sample text')


    def _handler(self, event: wx.KeyEvent) -> None:
        """
        Handle key up events.
        :param event: Used for getting key info.
        :return: None
        """
        event.Skip()
        if event.ControlDown() and event.GetKeyCode() == 86:
            # WXK_CONTROL_V is ctrl+v but only shows up in wx.TextCtrl, 86 is 'v' character code.
            print('text: ', self.rtc.GetValue())

    def _change_bold(self, evt: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        self.rtc.ApplyBoldToSelection()


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        # Required for copy paste to work and retain text attributes
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())

        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(400, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
