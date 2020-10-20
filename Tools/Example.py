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

        # Link style
        stl_link = rt.RichTextAttr()
        stl_link.SetFlags(wx.TEXT_ATTR_URL)
        stl_link.SetFontUnderlined(True)
        stl_link.SetTextColour(wx.BLUE)
        style_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition('url')
        style_link.SetStyle(stl_link)
        self._stylesheet.AddCharacterStyle(style_link)

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

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('par'))
        self.rtc.BeginParagraphStyle('par')
        self._insert_link('www.google.com', '42')
        self.rtc.WriteText(' paragraph 1, sample of a longer text for testing url creation ')
        self.rtc.LineBreak()
        self.rtc.WriteText('paragraph 1, more sample of a longer text for testing url creation ')
        self._insert_link('www.google.com', 'link from code')
        self.rtc.EndParagraphStyle()

        self.rtc.Newline()

        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('par'))
        self.rtc.BeginParagraphStyle('par')
        self._insert_link('www.google.com', '42')
        self.rtc.WriteText(' paragraph 2 adding some text after a link')
        self.rtc.LineBreak()
        self.rtc.WriteText(' some more text after a line break in code')
        self.rtc.EndParagraphStyle()

        self.rtc.Newline()


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
