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

        self.rtc.SetStyleSheet(self._stylesheet)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)

        self._create_styles()
        self._insert_sample_text()

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # List style
        stl_list: rt.RichTextAttr = rt.RichTextAttr()
        stl_list.SetFontSize(12)
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list.SetParagraphSpacingBefore(20)
        stl_list.SetParagraphSpacingAfter(20)
        stl_list.SetBackgroundColour(wx.GREEN)

        stl_list_1: rt.RichTextAttr = rt.RichTextAttr()
        stl_list_1.SetFontSize(12)
        stl_list_1.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list_1.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list_1.SetBulletStyle(wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
        stl_list_1.SetLeftIndent(20, 40)

        style_list: rt.RichTextListStyleDefinition = rt.RichTextListStyleDefinition('list')
        style_list.SetLevelAttributes(0, stl_list_1)
        style_list.SetStyle(stl_list)
        style_list.SetNextStyle('list')
        self._stylesheet.AddListStyle(style_list)

        self.rtc.SetStyleSheet(self._stylesheet)

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.BeginListStyle('list', 0)
        self.rtc.WriteText('Example list item 1')
        self.rtc.Newline()
        self.rtc.WriteText('Example list item 2')
        self.rtc.Newline()
        self.rtc.WriteText('Example list item 3')
        self.rtc.Newline()
        self.rtc.EndListStyle()

        self.rtc.BeginSymbolBullet('*', 20, 20, bulletStyle=wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
        self.rtc.WriteText('Example list item 1')
        self.rtc.Newline()
        self.rtc.WriteText('Example list item 1')
        self.rtc.Newline()
        self.rtc.EndSymbolBullet()


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