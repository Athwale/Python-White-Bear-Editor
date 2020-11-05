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

        self.style_control = rt.RichTextStyleComboCtrl(self, -1)
        self.rtc.SetStyleSheet(self._stylesheet)
        self.style_control.SetRichTextCtrl(self.rtc)
        self.style_control.SetStyleSheet(self._stylesheet)

        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self.style_control)
        self.SetSizer(self.sizer)

        self._create_styles()
        self._insert_sample_text()
        self.rtc.Bind(wx.EVT_KEY_UP, self.on_keypress, self.rtc)

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

    def _get_style_at_pos(self, position: int = 0) -> (str, bool):
        """
        Get the style name at given position in the text. 0 - current position, -1 - before current position 1 - after
        current position.
        :param position: The position.
        :return: Style name.
        """
        style_carrier = rt.RichTextAttr()
        self.rtc.GetStyle(position, style_carrier)
        if style_carrier.GetCharacterStyleName():
            # HasUrl()
            return style_carrier.GetCharacterStyleName()
        return style_carrier.GetParagraphStyleName()

    def on_keypress(self, event: wx.CommandEvent) -> None:
        """
        Run on key up.
        :param event:
        :return:
        """
        print('\ncurrent style from ctrl: ' + self.style_control.GetValue())
        current_position = self.rtc.GetCaretPosition()
        print('previous: ' + str(self._get_style_at_pos(current_position - 1)))
        print('current pos: ' + str(current_position) + ' ' + str(self._get_style_at_pos(current_position)))
        print('next: ' + str(self._get_style_at_pos(current_position + 1)))

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
