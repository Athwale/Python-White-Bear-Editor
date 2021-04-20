import wx
import wx.richtext as rt

from Constants.Constants import Strings


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._color_button = wx.Button(self, wx.ID_FILE1, 'color 1')
        self._color_button_1 = wx.Button(self, wx.ID_FILE2, 'color 2')
        self._bold_button = wx.Button(self, -1, 'bold')
        self._image_button = wx.Button(self, -1, 'image')
        self._refresh_button = wx.Button(self, -1, 'refresh')
        self._image_button.Disable()

        self._controls_sizer.Add(self._color_button)
        self._controls_sizer.Add(self._color_button_1)
        self._controls_sizer.Add(self._bold_button)
        self._controls_sizer.Add(self._image_button)
        self._controls_sizer.Add(self._refresh_button)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self._main_sizer.Add(self._controls_sizer)
        self.SetSizer(self._main_sizer)

        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button)
        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button_1)
        self.Bind(wx.EVT_BUTTON, self._change_bold, self._bold_button)

        self.Bind(wx.EVT_MENU, self._forward_event)

    def _change_color(self, evt: wx.CommandEvent) -> None:
        """
        Change text color to green
        :param evt: Not used
        :return: None
        """
        if evt.GetId() == wx.ID_FILE1:
            color = wx.Colour(234, 134, 88)
        else:
            color = wx.Colour(124, 144, 25)
        if self.rtc.HasSelection():
            self.rtc.BeginBatchUndo(Strings.undo_bold)
            color_range = self.rtc.GetSelectionRange()
            for char in range(color_range[0], color_range[1]):
                if char + 1 > color_range[1] + 1:
                    break
                single_range = rt.RichTextRange(char, char + 1)
                # Get the attributes of the single char range and modify them in place. Otherwise changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self.rtc.GetStyleForRange(single_range, attr)
                # Ignore links.
                if attr.HasURL():
                    continue
                attr.SetTextColour(color)
                self.rtc.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
            self.rtc.EndBatchUndo()
        else:
            self.rtc.BeginTextColour(color)

    def _change_bold(self, evt: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        self.rtc.ApplyBoldToSelection()

    def _forward_event(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)

    def insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        # todo try something with the forward event thing
        self.rtc.AppendText('Sample text\nSample text\nSample text')


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

        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(700, 700), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.insert_sample_text()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
