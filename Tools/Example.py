import wx
import wx.html
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

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Paragraph style
        stl_paragraph: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph.SetFlags(
            wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_WEIGHT | wx.TEXT_ATTR_PARA_SPACING_AFTER
            | wx.TEXT_ATTR_PARA_SPACING_BEFORE)
        stl_paragraph.SetFontSize(Numbers.paragraph_font_size)
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(0)
        stl_paragraph.SetParagraphSpacingAfter(0)

        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph)

        # Paragraph style 1
        stl_paragraph_1: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph_1.SetFlags(
            wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_WEIGHT | wx.TEXT_ATTR_PARA_SPACING_AFTER
            | wx.TEXT_ATTR_PARA_SPACING_BEFORE)
        stl_paragraph_1.SetFontSize(Numbers.paragraph_font_size_1)
        stl_paragraph_1.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph_1.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph_1.SetParagraphSpacingBefore(0)
        stl_paragraph_1.SetParagraphSpacingAfter(0)

        style_paragraph_1: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph_1)
        style_paragraph_1.SetStyle(stl_paragraph_1)
        style_paragraph_1.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph_1)

        # List style
        stl_list: rt.RichTextAttr = rt.RichTextAttr()
        stl_list.SetFlags(
            wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_WEIGHT | wx.TEXT_ATTR_PARA_SPACING_AFTER
            | wx.TEXT_ATTR_PARA_SPACING_BEFORE)
        stl_list.SetFontSize(Numbers.paragraph_font_size)
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list.SetParagraphSpacingBefore(Numbers.list_spacing)
        stl_list.SetParagraphSpacingAfter(Numbers.list_spacing)

        stl_list_1: rt.RichTextAttr = rt.RichTextAttr()
        stl_list_1.SetFlags(
            wx.TEXT_ATTR_FONT_SIZE | wx.TEXT_ATTR_ALIGNMENT | wx.TEXT_ATTR_FONT_WEIGHT | wx.TEXT_ATTR_PARA_SPACING_AFTER
            | wx.TEXT_ATTR_PARA_SPACING_BEFORE | wx.TEXT_ATTR_BULLET_STYLE | wx.TEXT_ATTR_LEFT_INDENT)
        stl_list_1.SetFontSize(Numbers.paragraph_font_size)
        stl_list_1.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list_1.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list.SetParagraphSpacingBefore(Numbers.list_spacing)
        stl_list.SetParagraphSpacingAfter(Numbers.list_spacing)
        stl_list_1.SetBulletStyle(wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
        stl_list_1.SetLeftIndent(Numbers.list_left_indent, Numbers.list_left_sub_indent)

        style_list: rt.RichTextListStyleDefinition = rt.RichTextListStyleDefinition(Strings.style_list)
        style_list.SetLevelAttributes(0, stl_list_1)
        style_list.SetStyle(stl_list)
        style_list.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddListStyle(style_list)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.EndParagraphStyle()
        self.rtc.Newline()

        self.rtc.BeginParagraphStyle(Strings.style_paragraph_1)
        self.rtc.WriteText('Example paragraph')
        self.rtc.EndParagraphStyle()
        self.rtc.Newline()

        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.EndParagraphStyle()
        self.rtc.Newline()

        #self.rtc.ApplyStyle(self._stylesheet.FindListStyle(Strings.style_list))
        self.rtc.BeginListStyle(Strings.style_list)
        for i in range(10):
            self.rtc.WriteText('Example list item')
            self.rtc.WriteText('\n')
        self.rtc.EndListStyle()

        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.EndParagraphStyle()
        self.rtc.Newline()


class Strings:
    """
    Just constants
    """
    style_paragraph: str = 'paragraph'
    style_paragraph_1: str = 'paragraph1'
    style_list: str = 'list'


class Numbers:
    list_spacing: int = 10
    paragraph_font_size: int = 12
    paragraph_font_size_1: int = 16
    list_left_indent: int = 30
    list_left_sub_indent: int = 30


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
