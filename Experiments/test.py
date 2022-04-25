
import wx
import wx.richtext as rt


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')
        self.rtc.SetStyleSheet(self._stylesheet)
        self._button = wx.Button(self, wx.ID_APPLY, 'Strike')
        self._button_1 = wx.Button(self, wx.ID_CANCEL, 'Unstrike')
        self.Bind(wx.EVT_BUTTON, self.strike_text, self._button)
        self.Bind(wx.EVT_BUTTON, self.strike_text, self._button_1)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self._button)
        self.sizer.Add(self._button_1)
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
        :param event: Used for button id.
        :return: None
        """
        strike = True
        if event.GetId() == wx.ID_CANCEL:
            strike = False

        self.rtc.BeginSuppressUndo()
        # The word selection would move the caret if the position was not restored.
        position = self.rtc.GetCaretPosition()
        # Remove all striking from anything that was stricken previously.
        self.rtc.SelectAll()
        self.apply_effect(False, self.rtc.GetSelectionRange())
        self.rtc.SelectNone()

        word_range = rt.RichTextRange(5, 9)
        self.apply_effect(strike, word_range)

        self.rtc.SetCaretPosition(position)
        self.rtc.EndSuppressUndo()

    def apply_effect(self, enable: bool, text_range: rt.RichTextRange) -> None:
        """
        Apply text effect to range of characters.
        :param enable: True to turn effect on.
        :param text_range: Range for the effect.
        :return: None
        """
        # TODO red wavy spellcheck underline is not implemented yet.
        effect = wx.TEXT_ATTR_EFFECT_STRIKETHROUGH
        attrs: rt.RichTextAttr = rt.RichTextAttr()
        attrs.SetFlags(wx.TEXT_ATTR_EFFECTS)
        attrs.SetTextEffectFlags(effect)
        if enable:
            attrs.SetTextEffects(effect)
        else:
            attrs.SetTextEffects(attrs.GetTextEffectFlags() & ~effect)
        self.rtc.SetStyleEx(text_range, attrs)

    def _insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle('paragraph'))
        self.rtc.BeginParagraphStyle('paragraph')
        self.rtc.WriteText('Test text that shows an odd behavior.')
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
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(500, 300), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
