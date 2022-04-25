
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
        self._button = wx.Button(self, -1, 'Strike')
        self.Bind(wx.EVT_BUTTON, self.strike_text, self._button)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self._button)
        self.SetSizer(self.sizer)

        self._create_styles()
        self._insert_sample_text()

    def _create_styles(self) -> None:
        """
        Create styles for rich text control.
        :return: None
        """
        # Normal style
        stl_paragraph: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph.SetFontSize(12)
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(0)
        stl_paragraph.SetParagraphSpacingAfter(0)
        stl_paragraph.SetParagraphStyleName('par')
        stl_paragraph.SetFontFaceName('par')
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition('paragraph')
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle('paragraph')
        self._stylesheet.AddParagraphStyle(style_paragraph)
        self.rtc.ApplyStyle(style_paragraph)
        self.rtc.SetDefaultStyle(stl_paragraph)

    def strike_text(self, event: wx.CommandEvent) -> None:
        """
        Strike a range of text.
        :param event: Unused.
        :return: None
        """
        self.rtc.BeginSuppressUndo()
        # The word selection would move the caret if the position was not restored.
        position = self.rtc.GetCaretPosition()
        # Apply twice to remove and reapply
        self.rtc.SelectAll()
        self.apply_effect(False, self.rtc.GetSelectionRange())
        self.rtc.SelectNone()

        word_range = rt.RichTextRange(5, 10)
        self.apply_effect(True, word_range)

        self.rtc.SetCaretPosition(position)
        self.rtc.EndSuppressUndo()

    def apply_effect(self, enable: bool, text_range: rt.RichTextRange) -> None:
        """
        Apply text effect to range of characters.
        :param enable: True to turn effect on.
        :param text_range: Range for the effect.
        :return: None
        """
        # TODO red spellcheck underline is not implemented yet.
        effect = wx.TEXT_ATTR_EFFECT_STRIKETHROUGH
        attrs: rt.RichTextAttr = rt.RichTextAttr()
        attr = rt.RichTextAttr()
        self.rtc.GetStyleForRange(text_range, attr)
        if enable:
            attrs.SetFlags(wx.TEXT_ATTR_EFFECTS)
            attrs.SetTextEffects(effect)
            attrs.SetTextEffectFlags(effect)
        else:
            attrs.SetFlags(attrs.GetFlags() & ~wx.TEXT_ATTR_EFFECTS)
            attrs.SetTextEffects(attrs.GetTextEffectFlags() & ~effect)
            attrs.SetTextEffectFlags(attrs.GetTextEffectFlags() & ~effect)
        self.rtc.SetStyleEx(text_range, attrs, rt.RICHTEXT_SETSTYLE_OPTIMIZE | rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('paragraph'))
        self.rtc.BeginParagraphStyle('paragraph')
        self.rtc.WriteText('Paragraph adding some text')
        self.rtc.WriteText(' some more text after a link')
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
