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

        self._style_control = rt.RichTextStyleListBox(self, 1, size=(140, 25))
        self._style_control.SetStyleType(0)
        self._style_control.SetMargins(-5, -5)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)

        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self._style_control)
        self.SetSizer(self.sizer)

        self._create_styles()
        self._insert_sample_text()

        self.rtc.Bind(wx.EVT_KEY_UP, self.on_keypress)

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Paragraph style
        stl_paragraph: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph.SetFontSize(Numbers.paragraph_font_size)
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
        stl_paragraph.SetParagraphSpacingAfter(Numbers.paragraph_spacing)

        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_par)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_par)
        self._stylesheet.AddParagraphStyle(style_paragraph)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_par))
        self.rtc.BeginParagraphStyle(Strings.style_par)
        self.rtc.WriteText('Example paragraph')
        self.rtc.EndParagraphStyle()
        self.rtc.Newline()

    def on_keypress(self, evt: wx.KeyEvent) -> None:
        """
        Capture key presses
        :param evt: Carries the key code.
        :return: None
        """
        print(evt.GetKeyCode())


class Strings:
    """
    Just constants
    """
    style_par: str = 'paragraph'


class Numbers:
    paragraph_font_size: int = 12
    paragraph_spacing: int = 10


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(900, 700), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
