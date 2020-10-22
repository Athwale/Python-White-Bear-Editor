import wx
import os
import wx.richtext as rt


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')
        self._create_styles()
        self._insert_sample_text()

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Normal style
        stl_paragraph: rt.RichTextAttr = self.rtc.GetDefaultStyleEx()
        stl_paragraph.SetParagraphSpacingBefore(10)
        stl_paragraph.SetParagraphSpacingAfter(10)
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition('par')
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle('par')
        self._stylesheet.AddParagraphStyle(style_paragraph)
        self.rtc.ApplyStyle(style_paragraph)
        self.rtc.SetDefaultStyle(stl_paragraph)

        # Heading 3 style
        stl_heading_3: rt.RichTextAttr = self.rtc.GetDefaultStyleEx()
        stl_heading_3.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_3.SetFontWeight(wx.BOLD)
        stl_heading_3.SetFontSize(18)
        stl_heading_3.SetParagraphSpacingAfter(25)
        style_h3: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition('title')
        style_h3.SetStyle(stl_heading_3)
        style_h3.SetNextStyle('par')
        self._stylesheet.AddParagraphStyle(style_h3)

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('title'))
        self.rtc.BeginParagraphStyle('title')
        self.rtc.WriteText('Title')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('par'))
        self.rtc.BeginParagraphStyle('par')
        self.rtc.WriteText(' paragraph 2 adding some text after a link')
        self.rtc.LineBreak()
        self.rtc.WriteText(' some more text after a line break in code')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()


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
