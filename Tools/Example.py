import wx
import wx.richtext as rt


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Create style stylesheet and control
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')

        self.style_control = rt.RichTextStyleListBox(self, 1, size=(140, 60))
        self.style_control.SetStyleType(0)
        self.style_control.SetMargins(-5, -5)

        self.rtc.SetStyleSheet(self._stylesheet)
        self.style_control.SetRichTextCtrl(self.rtc)
        self.style_control.SetStyleSheet(self._stylesheet)

        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self.style_control)
        self.SetSizer(self.sizer)

        self._create_styles()
        self._insert_sample_text()
        self.rtc.Bind(wx.EVT_KEY_UP, self.on_keypress, self.rtc)
        self.rtc.Bind(wx.EVT_TEXT_URL, self.url_in_text_click_handler, self.rtc)

    @staticmethod
    def url_in_text_click_handler(evt: wx.TextUrlEvent) -> None:
        """
        Handles click on url links inside text.
        :param evt: Not used
        :return: None
        """
        print(evt.GetString(), evt.GetURLStart(), evt.GetURLEnd())

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Normal style
        stl_paragraph: rt.RichTextAttr = self.rtc.GetDefaultStyleEx()
        stl_paragraph.SetParagraphSpacingBefore(10)
        stl_paragraph.SetParagraphSpacingAfter(10)
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition('paragraph')
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle('paragraph')
        self._stylesheet.AddParagraphStyle(style_paragraph)
        self.rtc.ApplyStyle(style_paragraph)
        self.rtc.SetDefaultStyle(stl_paragraph)

        # Link style
        stl_link = rt.RichTextAttr()
        stl_link.SetFlags(wx.TEXT_ATTR_URL)
        stl_link.SetFontUnderlined(True)
        stl_link.SetTextColour(wx.BLUE)
        style_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition('url')
        style_link.SetStyle(stl_link)
        self._stylesheet.AddCharacterStyle(style_link)
        self.style_control.UpdateStyles()

    def _insert_link(self, text: str, link_id: str) -> None:
        """
        Insert a link into text at current position.
        :param text: The visible text.
        :param link_id: The ID of the link
        :return: None
        """
        self.rtc.BeginStyle(self._stylesheet.FindCharacterStyle('url').GetStyle())
        self.rtc.BeginURL(link_id)
        self.rtc.WriteText(text)
        self.rtc.EndURL()
        self.rtc.EndStyle()
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('paragraph'))

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('paragraph'))
        self.rtc.BeginParagraphStyle('paragraph')
        self.rtc.WriteText('Paragraph adding some text ')
        self._insert_link('google', 'fe80')
        self.rtc.WriteText(' some more text after a link')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

    def on_keypress(self, event: wx.CommandEvent) -> None:
        """
        Run on key up.
        :param event:
        :return:
        """
        current_style = str(self.style_control.GetStyle(self.style_control.GetSelection()).GetName())
        print(current_style)
        event.Skip()


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(900, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
