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

        self._style_control = rt.RichTextStyleListBox(self, 1, size=(140, 60))
        self._style_control.SetApplyOnSelection(True)
        self._style_control.SetStyleType(0)
        self._style_control.SetMargins(-5, -5)

        self._button = wx.Button(self, -1, 'Apply bold style')
        self.Bind(wx.EVT_BUTTON, self._style_button_handler, self._button)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)

        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self._style_control)
        self.sizer.Add(self._button)
        self.SetSizer(self.sizer)

        self._create_styles()

    def _style_button_handler(self, evt: wx.CommandEvent) -> None:
        """
        Handles button clicks.
        :param evt: Not used
        :return: None
        """
        style = self._stylesheet.FindParagraphStyle(Strings.style_paragraph_bold).GetStyle()
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(self.rtc.GetCaretPosition()+1)
        self.rtc.SetStyleEx(p.GetRange().FromInternal(), style, flags=rt.RICHTEXT_SETSTYLE_RESET |
                            rt.RICHTEXT_SETSTYLE_OPTIMIZE | rt.RICHTEXT_SETSTYLE_WITH_UNDO)

        # This calls the SetStyleEx function later on according to c++ code
        # self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph_bold))

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Paragraph style
        stl_paragraph: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph.SetFontSize(Numbers.paragraph_font_size)
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        # todo font weight and size is ignored
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
        stl_paragraph.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        stl_paragraph.SetBackgroundColour(wx.GREEN)
        stl_paragraph.SetParagraphStyleName(Strings.style_paragraph)
        stl_paragraph.SetFlags(wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_FONT_WEIGHT |
                               wx.TEXT_ATTR_PARA_SPACING_AFTER | wx.TEXT_ATTR_PARA_SPACING_BEFORE |
                               wx.TEXT_ATTR_BACKGROUND_COLOUR | wx.TEXT_ATTR_PARAGRAPH_STYLE_NAME ^ rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY ^ rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)

        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph)

        # Paragraph style bold
        stl_paragraph_bold: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph_bold.SetFontSize(Numbers.paragraph_font_size_1)
        stl_paragraph_bold.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph_bold.SetFontWeight(wx.FONTWEIGHT_BOLD)
        stl_paragraph_bold.SetParagraphSpacingBefore(Numbers.paragraph_spacing_bold)
        stl_paragraph_bold.SetParagraphSpacingAfter(Numbers.paragraph_spacing_bold)
        stl_paragraph_bold.SetBackgroundColour(wx.YELLOW)
        stl_paragraph.SetParagraphStyleName(Strings.style_paragraph_bold)
        stl_paragraph_bold.SetFlags(wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_FONT_WEIGHT |
                                    wx.TEXT_ATTR_PARA_SPACING_AFTER | wx.TEXT_ATTR_PARA_SPACING_BEFORE |
                                    wx.TEXT_ATTR_BACKGROUND_COLOUR | wx.TEXT_ATTR_PARAGRAPH |
                                    wx.TEXT_ATTR_PARAGRAPH_STYLE_NAME ^ rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY ^ rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)

        style_paragraph_bold: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph_bold)
        style_paragraph_bold.SetStyle(stl_paragraph_bold)
        style_paragraph_bold.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph_bold)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()
        self.rtc.SetDefaultStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph).GetStyle())

    def insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        # self._style_control.ApplyStyle(0)
        # self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        # self.rtc.Newline()
        # self.rtc.EndParagraphStyle()

        # self.rtc.BeginParagraphStyle(Strings.style_paragraph_bold)
        # self.rtc.WriteText('Example paragraph')
        # self.rtc.Newline()
        # self.rtc.EndParagraphStyle()

        # self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        # self.rtc.WriteText('Example paragraph')
        # self.rtc.Newline()
        # self.rtc.EndParagraphStyle()

        self.rtc.Newline()

        self.rtc.LayoutContent()


class Strings:
    """
    Just constants
    """
    style_paragraph: str = 'paragraph'
    style_paragraph_bold: str = 'boldparagraph'


class Numbers:
    paragraph_font_size: int = 10
    paragraph_font_size_1: int = 20
    paragraph_spacing: int = 20
    paragraph_spacing_bold: int = 50


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
        self.frame.insert_sample_text()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
