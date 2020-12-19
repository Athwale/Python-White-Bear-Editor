import wx
import wx.richtext as rt

from Constants.Constants import Strings, Numbers


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create style stylesheet and control
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')

        self._style_control = rt.RichTextStyleListBox(self, 1, size=(100, 160))
        self._style_control.SetStyleType(0)
        self._style_control.SetMargins(-5, -5)
        self._style_control.Enable(False)

        self._style_picker = wx.ListBox(self, -1, size=(100, 160))

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._color_button = wx.Button(self, -1, 'green')
        self._bold_button = wx.Button(self, -1, 'bold')

        self._controls_sizer.Add(self._style_control)
        self._controls_sizer.Add(self._style_picker)
        self._controls_sizer.Add(self._color_button)
        self._controls_sizer.Add(self._bold_button)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self._main_sizer.Add(self._controls_sizer)
        self.SetSizer(self._main_sizer)

        self.Bind(wx.EVT_LISTBOX, self._change_style, self._style_picker)
        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button)
        self.Bind(wx.EVT_BUTTON, self._change_bold, self._bold_button)
        self.rtc.Bind(wx.EVT_KEY_UP, self.on_keypress)

        self._create_styles()
        self._fill_picker()

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
        stl_paragraph.SetParagraphSpacingBefore(0)
        stl_paragraph.SetParagraphSpacingAfter(0)

        stl_paragraph.SetBackgroundColour(wx.YELLOW)

        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph)

        # Heading 3 style
        stl_heading_3: rt.RichTextAttr = rt.RichTextAttr()
        stl_heading_3.SetFontSize(Numbers.heading_3_size)
        stl_heading_3.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_3.SetFontWeight(wx.FONTWEIGHT_BOLD)
        stl_heading_3.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
        stl_heading_3.SetParagraphSpacingAfter(Numbers.paragraph_spacing)

        stl_heading_3.SetBackgroundColour(wx.RED)

        style_h3: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_3)
        style_h3.SetStyle(stl_heading_3)
        style_h3.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h3)

        # Heading 4 style
        stl_heading_4: rt.RichTextAttr = rt.RichTextAttr()
        stl_heading_4.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_4.SetFontWeight(wx.FONTWEIGHT_BOLD)
        stl_heading_4.SetParagraphSpacingBefore(Numbers.paragraph_spacing / 2)
        stl_heading_4.SetParagraphSpacingAfter(Numbers.paragraph_spacing / 2)

        stl_heading_4.SetBackgroundColour(wx.BLUE)

        style_h4: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_4)
        style_h4.SetStyle(stl_heading_4)
        style_h4.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h4)

        # Image style
        stl_image: rt.RichTextAttr = rt.RichTextAttr()
        stl_image.SetFontSize(Numbers.paragraph_font_size)
        stl_image.SetAlignment(wx.TEXT_ALIGNMENT_CENTER)
        stl_image.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_image.SetParagraphSpacingAfter(Numbers.image_spacing)
        stl_image.SetParagraphSpacingBefore(Numbers.image_spacing)

        style_image: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_image)
        style_image.SetStyle(stl_image)
        style_image.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_image)

        # List style
        stl_list: rt.RichTextAttr = rt.RichTextAttr()
        stl_list.SetFontSize(Numbers.paragraph_font_size)
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list.SetParagraphSpacingBefore(Numbers.list_spacing)
        stl_list.SetParagraphSpacingAfter(Numbers.list_spacing)

        stl_list.SetBackgroundColour(wx.GREEN)

        stl_list_1: rt.RichTextAttr = rt.RichTextAttr()
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

        # Link style
        stl_link = rt.RichTextAttr()
        stl_link.SetURL(Strings.link_stub)
        stl_link.SetFontUnderlined(True)
        stl_link.SetTextColour(wx.BLUE)
        stl_link.SetBackgroundColour(wx.RED)
        style_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition(Strings.style_url)
        style_link.SetStyle(stl_link)
        self._stylesheet.AddCharacterStyle(style_link)

        self.rtc.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self.rtc)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()

    def _fill_picker(self) -> None:
        """
        Fill picker list box with style names
        :return: None
        """
        names = []
        for n in range(self._stylesheet.GetParagraphStyleCount()):
            names.append(self._stylesheet.GetParagraphStyle(n).GetName())
        for n in range(self._stylesheet.GetListStyleCount()):
            names.append(self._stylesheet.GetListStyle(n).GetName())
        for n in range(self._stylesheet.GetListStyleCount()):
            names.append(self._stylesheet.GetCharacterStyle(n).GetName())

        self._style_picker.InsertItems(names, 0)

    def _change_color(self, evt: wx.CommandEvent) -> None:
        """
        Change text color to green
        :param evt: Not used
        :return: None
        """
        attr = rt.RichTextAttr()
        r = self.rtc.GetSelectionRange()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        attr.SetTextColour(wx.GREEN)
        self.rtc.SetStyleEx(r, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)

    def _change_bold(self, evt: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        if self.rtc.HasSelection():
            bold_range = self.rtc.GetSelectionRange()
            attr = rt.RichTextAttr()
            attr.SetFlags(wx.TEXT_ATTR_FONT_WEIGHT)
            attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            self.rtc.SetStyleEx(bold_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)

    def _change_paragraph_style(self, style: rt.RichTextAttr, paragraphs_only: bool) -> None:
        """
        Change the current paragraph into the paragraph style from parameter without destroying urls.
        :param style: The paragraph style
        :param paragraphs_only: Limit style to paragraphs
        :return: None
        """
        paragraphs_flag = 0
        if paragraphs_only:
            paragraphs_flag = rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
            self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
        self.rtc.SetStyleEx(p.GetRange().FromInternal(), style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | paragraphs_flag)

    def _change_style(self, evt: wx.CommandEvent) -> None:
        """
        Handles button clicks.
        :param evt: The name of the style in stylesheet
        :return: None
        """
        style: rt.RichTextAttr = self._stylesheet.FindStyle(evt.GetString()).GetStyle()
        style_name = evt.GetString()

        if style_name == Strings.style_heading_3 or style_name == Strings.style_heading_4:
            # When changing into heading, we reset everything and remove any list style.
            p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
                self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
            # Reset any url character style too, it will not disappear if only paragraph style is reset.
            url_style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
            self.rtc.SetStyleEx(p.GetRange(), url_style, rt.RICHTEXT_SETSTYLE_REMOVE)
            # Change the paragraph style into a heading style.
            self.rtc.ClearListStyle(p.GetRange())
            self._change_paragraph_style(style, False)

        elif style_name == Strings.style_paragraph:
            # When switching from heading style, disable limit to paragraph only since we want to get rid of the
            # heading style attributes completely.
            paragraph_only_flag = True
            current_style = self._get_style_at_pos(self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
            if current_style == Strings.style_heading_3 or current_style == Strings.style_heading_4:
                paragraph_only_flag = False
            p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
                self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
            self.rtc.ClearListStyle(p.GetRange())
            self._change_paragraph_style(style, paragraph_only_flag)

        elif style_name == Strings.style_list:
            # When switching from heading style, disable limit to paragraph only since we want to get rid of the
            # heading style attributes completely. When changing text into list, change everything into list style
            # first to get rid of other styles.
            paragraph_only_flag = True
            current_style = self._get_style_at_pos(self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
            if current_style == Strings.style_heading_3 or current_style == Strings.style_heading_4:
                paragraph_only_flag = False
            # Reset to paragraph style to get rid of any extra styles
            paragraph_style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_paragraph).GetStyle()
            self._change_paragraph_style(paragraph_style, paragraph_only_flag)

            p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
                self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
            self.rtc.SetListStyle(p.GetRange(), self._stylesheet.FindStyle(evt.GetString()),
                                  flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL,
                                  specifiedLevel=0)

        # TODO reapply style on delete and backspace to get rid of mixed styles.
        # TODO get style on pos on mouse click

        elif style_name == Strings.style_image:
            print('img')

        else:
            # URL Character style
            if self.rtc.HasSelection():
                link_range = self.rtc.GetSelectionRange()
                self.rtc.SetStyleEx(link_range, self._stylesheet.FindStyle(evt.GetString()).GetStyle(),
                                    flags=rt.RICHTEXT_SETSTYLE_RESET | rt.RICHTEXT_SETSTYLE_OPTIMIZE |
                                          rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)

    def _get_style_at_pos(self, position: int = 0) -> (str, str):
        """
        Get the style name at given position in the text. 0 - current position, -1 - before current position
        1 - after current position.
        :param position: The position.
        :return: (paragraph style name, character style name) or (None, None).
        """
        style_carrier = rt.RichTextAttr()
        paragraph_style_name = None
        character_style_name = None
        self.rtc.GetStyle(position, style_carrier)
        if style_carrier.GetCharacterStyleName():
            character_style_name = style_carrier.GetCharacterStyleName()
        if style_carrier.GetListStyleName():
            paragraph_style_name = style_carrier.GetListStyleName()
        if style_carrier.GetParagraphStyleName():
            paragraph_style_name = style_carrier.GetParagraphStyleName()
        # Set the current style name into the style list box.
        self._style_picker.SetSelection(self._style_picker.FindString(paragraph_style_name))
        return paragraph_style_name, character_style_name

    def on_keypress(self, event):
        """
        :param event:
        :return:
        """
        print('adjusted style name: ' + str(self._get_style_at_pos(self.rtc.GetAdjustedCaretPosition(self.rtc.
                                                                                                 GetCaretPosition()))))
        print('from ctrl: ' + self._style_control.GetStyle(self._style_control.GetSelection()).GetName())
        current_position = self.rtc.GetCaretPosition()
        print('pos: ' + str(current_position))
        print('previous: ' + str(
            str(self._get_style_at_pos(current_position - 1)) + ' ' + self.rtc.GetRange(current_position - 1,
                                                                                        current_position)))
        print('current: ' + str(
            str(self._get_style_at_pos(current_position + 1)) + ' ' + self.rtc.GetRange(current_position,
                                                                                        current_position + 1)))
        print('next: ' + str(
            str(self._get_style_at_pos(current_position + 2)) + ' ' + self.rtc.GetRange(current_position + 1,
                                                                                        current_position + 2)))
        event.Skip()

    def insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.BeginParagraphStyle(Strings.style_heading_3)
        self.rtc.WriteText('Example paragraph')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.Newline()

        self.rtc.LayoutContent()


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
