import wx
import wx.richtext as rt

from Constants.Constants import Strings, Numbers
from Tools.Document.ArticleElements.Video import Video
from Tools.ImageTextField import ImageTextField


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create style stylesheet and control
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')

        self._style_picker = wx.ListBox(self, -1, size=(100, 160))
        self._previous_style: str = Strings.style_paragraph

        self.rtc.SetStyleSheet(self._stylesheet)
        self._color_button = wx.Button(self, -1, 'color')
        self._bold_button = wx.Button(self, -1, 'bold')
        self._image_button = wx.Button(self, -1, 'image')
        self._refresh_button = wx.Button(self, -1, 'refresh')
        self._image_button.Disable()

        self._controls_sizer.Add(self._style_picker)
        self._controls_sizer.Add(self._color_button)
        self._controls_sizer.Add(self._bold_button)
        self._controls_sizer.Add(self._image_button)
        self._controls_sizer.Add(self._refresh_button)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self._main_sizer.Add(self._controls_sizer)
        self.SetSizer(self._main_sizer)

        self.Bind(wx.EVT_LISTBOX, self._style_picker_handler, self._style_picker)
        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button)
        self.Bind(wx.EVT_BUTTON, self._change_bold, self._bold_button)
        self.Bind(wx.EVT_BUTTON, self._write_field, self._image_button)
        self.Bind(wx.EVT_BUTTON, self._refresh, self._refresh_button)

        self.rtc.Bind(wx.EVT_LEFT_UP, self._on_mouse)
        self.rtc.Bind(wx.EVT_MOUSE_EVENTS, self._on_mouse)

        self.rtc.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.rtc.Bind(wx.EVT_TEXT, self._text_evt_handler)
        self.rtc.Bind(wx.EVT_CHAR, self._on_key)

        self.rtc.GetBuffer().CleanUpFieldTypes()
        self._create_styles()
        self._fill_style_picker()

    def _refresh(self, evt: wx.CommandEvent) -> None:
        """
        Refresh the text field.
        :param evt: Not used
        :return: None
        """
        self.rtc.Invalidate()
        self.rtc.Refresh()

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
        stl_paragraph.SetParagraphStyleName(Strings.style_paragraph)
        # Used to identify text object children of paragraphs
        stl_paragraph.SetFontFaceName(Strings.style_paragraph)

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
        stl_heading_3.SetParagraphStyleName(Strings.style_heading_3)
        stl_heading_3.SetFontFaceName(Strings.style_heading_3)

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
        stl_heading_4.SetParagraphStyleName(Strings.style_heading_4)
        stl_heading_4.SetFontFaceName(Strings.style_heading_4)

        stl_heading_4.SetBackgroundColour(wx.BLUE)

        style_h4: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_4)
        style_h4.SetStyle(stl_heading_4)
        style_h4.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h4)

        # List style
        stl_list: rt.RichTextAttr = rt.RichTextAttr()
        stl_list.SetFontSize(Numbers.paragraph_font_size)
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list.SetParagraphSpacingBefore(Numbers.list_spacing)
        stl_list.SetParagraphSpacingAfter(Numbers.list_spacing)
        stl_list.SetListStyleName(Strings.style_list)
        stl_list.SetFontFaceName(Strings.style_list)

        stl_list.SetBackgroundColour(wx.GREEN)

        stl_list_1: rt.RichTextAttr = rt.RichTextAttr()
        stl_list_1.SetFontSize(Numbers.paragraph_font_size)
        stl_list_1.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list_1.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_list_1.SetBulletStyle(wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
        stl_list_1.SetLeftIndent(Numbers.list_left_indent, Numbers.list_left_sub_indent)
        stl_list_1.SetListStyleName(Strings.style_list)
        stl_list.SetFontFaceName(Strings.style_list)

        style_list: rt.RichTextListStyleDefinition = rt.RichTextListStyleDefinition(Strings.style_list)
        style_list.SetLevelAttributes(0, stl_list_1)
        style_list.SetStyle(stl_list)
        style_list.SetNextStyle(Strings.style_list)
        self._stylesheet.AddListStyle(style_list)

        # Link style
        stl_link = rt.RichTextAttr()
        stl_link.SetURL(Strings.link_stub)
        stl_link.SetFontUnderlined(True)
        stl_link.SetTextColour(wx.BLUE)
        stl_link.SetBackgroundColour(wx.RED)
        stl_link.SetCharacterStyleName(Strings.style_link)
        stl_link.SetFontFaceName(Strings.style_link)
        style_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition(Strings.style_url)
        style_link.SetStyle(stl_link)
        self._stylesheet.AddCharacterStyle(style_link)

        # Image style
        # Add the image style even though we do not use it from the style picker, this allows easy next style
        # definition.
        stl_image: rt.RichTextAttr = rt.RichTextAttr()
        stl_image.SetFontSize(Numbers.paragraph_font_size)
        stl_image.SetAlignment(wx.TEXT_ALIGNMENT_CENTER)
        stl_image.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_image.SetParagraphSpacingAfter(Numbers.image_spacing)
        stl_image.SetParagraphSpacingBefore(Numbers.image_spacing)
        stl_image.SetParagraphStyleName(Strings.style_image)
        stl_image.SetFontFaceName(Strings.style_image)

        style_image: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_image)
        style_image.SetStyle(stl_image)
        style_image.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_image)

        self.rtc.SetStyleSheet(self._stylesheet)

    def _fill_style_picker(self) -> None:
        """
        Fill picker list box with style names
        :return: None
        """
        names = []
        for n in range(self._stylesheet.GetParagraphStyleCount()):
            if self._stylesheet.GetParagraphStyle(n).GetName() != Strings.style_image:
                # Ignore the image style.
                names.append(self._stylesheet.GetParagraphStyle(n).GetName())
        # There is only one list style
        names.append(Strings.style_list)
        names.append(Strings.style_url)

        self._style_picker.InsertItems(names, 0)

    def _change_paragraph_style(self, new_style: rt.RichTextAttr, paragraphs_only: bool,
                                remove: bool, position=None) -> None:
        """
        Change the current paragraph into the paragraph style from parameter without destroying urls.
        :param new_style: The paragraph style
        :param paragraphs_only: Limit style to paragraphs
        :param remove: Remove the style from the current paragraph.
        :param position: The position where to change the paragraph. If None, current paragraph is used.
        :return: None
        """
        if not position:
            position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        par_flag = 0
        remove_flag = 0
        if paragraphs_only:
            par_flag = rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
        if remove:
            remove_flag = rt.RICHTEXT_SETSTYLE_REMOVE
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        self.rtc.SetStyleEx(p.GetRange().FromInternal(), new_style,
                            flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | par_flag | remove_flag | rt.RICHTEXT_SETSTYLE_RESET)

    def _change_style(self, style_name: str, force_paragraph=False) -> None:
        """
        Changes the style of the current paragraph or selection.
        :param style_name: The name of a style in stylesheet.
        :param force_paragraph: Used in setting paragraph style to override whether character style should be set too.
        This is used when joining heading and ordinary paragraph using delete or backspace.
        :return: None
        """
        if style_name == Strings.style_heading_3 or style_name == Strings.style_heading_4:
            self._apply_heading_style(style_name)

        elif style_name == Strings.style_paragraph:
            self._apply_paragraph_style()

        elif style_name == Strings.style_list:
            self._apply_list_style()

        else:
            self._apply_url_style()

        self._update_style_picker()

    def _apply_heading_style(self, heading_type: str) -> None:
        """
        Changes current paragraph under the cursor into a heading 3 or 4, removing any links.
        :param heading_type: The heading style size.
        :return: None
        """
        style: rt.RichTextAttr = self._stylesheet.FindStyle(heading_type).GetStyle()
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
            self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
        # Brute force the paragraph into the heading style both paragraph and character attributes. This removes all
        # other style attributes except URL flag.
        self.rtc.SetStyleEx(p.GetRange().FromInternal(), style,
                            flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_RESET)
        # The paragraph changes after style set, so find it again.
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
            self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
        for child in p.GetChildren():
            # If any child has a url flag, remove it.
            attrs: rt.RichTextAttr = child.GetAttributes()
            if attrs.HasURL():
                # TODO try save, this might still appear in xml if we use it. How is other url remove going to work?
                attrs.SetURL('')
                attrs.SetFlags(attrs.GetFlags() ^ wx.TEXT_ATTR_URL)

    def _apply_paragraph_style(self) -> None:
        """
        Changes current paragraph under the cursor into the paragraph style defined for normal text.
        Retains links, text weight and color.
        :return: None
        """
        style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_paragraph).GetStyle()
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
            self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
        # Save text children attributes to restore them after forcing the paragraph style.
        # We need text weight, color, background, underline. URL flag remains untouched. Font size will be replaced by
        # the paragraph style.
        child_list = []
        for child in p.GetChildren():
            saved_attrs = {}
            # The build in wx Copy method causes the children to disappear for a wtf reason.
            attrs: rt.RichTextAttr = child.GetAttributes()
            if attrs.GetFontFaceName() == Strings.style_heading_3 or attrs.GetFontFaceName() == Strings.style_heading_4:
                # Do not save bold font weight from heading style.
                saved_attrs['weight'] = wx.FONTWEIGHT_NORMAL
            else:
                saved_attrs['weight'] = attrs.GetFontWeight()
            saved_attrs['color'] = attrs.GetTextColour()
            saved_attrs['background'] = attrs.GetBackgroundColour()
            saved_attrs['underlined'] = attrs.GetFontUnderlined()
            child_list.append(saved_attrs)
        # Brute force the paragraph into the paragraph style both paragraph and character attributes. This removes all.
        # other style attributes except URL flag.
        self.rtc.SetStyleEx(p.GetRange().FromInternal(), style,
                            flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_RESET)
        # The paragraph changes after style set, so find it again.
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(
            self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))
        # Restore only relevant attributes to the new children. The order is the same.
        for child, attr_dict in zip(p.GetChildren(), child_list):
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontWeight(attr_dict['weight'])
            attrs.SetTextColour(attr_dict['color'])
            if attrs.HasURL():
                # Only urls have background color and underline.
                attrs.SetBackgroundColour(attr_dict['background'])
                attrs.SetFontUnderlined(attr_dict['underlined'])

    def _apply_list_style(self, position=None) -> None:
        """
        Changes paragraph on position into list item.
        :param position: Where to apply the style, if not set, current paragraph is used.
        :return: None
        """
        # This is used to keep the list style going when return key is pressed. We move one position back and reapply
        # the style there. In other cases we want to apply the style in the current paragraph.
        if not position:
            position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        # When switching from heading style, disable limit to paragraph only since we want to get rid of the
        # heading style attributes completely. When changing text into list, change everything into list style
        # first to get rid of other styles.
        paragraph_only_flag = True
        current_style = self._get_style_at_pos(self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition()))[0]
        if current_style == Strings.style_heading_3 or current_style == Strings.style_heading_4:
            paragraph_only_flag = False

        # Reset to list style to get rid of any extra styles
        list_style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_list).GetStyle()
        self._change_paragraph_style(list_style, paragraphs_only=paragraph_only_flag, remove=False,
                                     position=position)

        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        self.rtc.SetListStyle(p.GetRange(), self._stylesheet.FindStyle(Strings.style_list),
                              flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL,
                              specifiedLevel=0)

    def _apply_url_style(self) -> None:
        """
        Changes current selection the url character style.
        :return: None
        """
        if self.rtc.HasSelection():
            link_range = self.rtc.GetSelectionRange()
            self.rtc.SetStyleEx(link_range, self._stylesheet.FindStyle(Strings.style_url).GetStyle(),
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
        return paragraph_style_name, character_style_name

    def _update_style_picker(self):
        """
        Show current style under cursor in the style box.
        """
        paragraph_style_name, character_style_name = self._get_style_at_pos(self.rtc.GetAdjustedCaretPosition
                                                                            (self.rtc.GetCaretPosition()))
        if character_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(character_style_name))
        elif paragraph_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(paragraph_style_name))
        # Return focus back into the text area. The focus must happen a little later when the style picker is finished.
        wx.CallLater(100, self.rtc.SetFocus)

    def _modify_text(self, key_code) -> None:
        """
        Handle key up events.
        :param key_code: Wxpython WXK key code.
        :return: None
        """
        self._update_style_picker()
        self._enable_buttons()
        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        paragraph_style, character_style = self._get_style_at_pos(position)
        if character_style == Strings.style_url and key_code == wx.WXK_SPACE:
            # End url style if next character has different or no url.
            style_carrier = rt.RichTextAttr()
            self.rtc.GetStyle(position, style_carrier)
            current_url = style_carrier.GetURL()
            self.rtc.GetStyle(position + 1, style_carrier)
            next_url = style_carrier.GetURL()
            if not next_url or current_url != next_url or position == (p.GetRange()[1] - 1):
                # End url style if we are at th end of a url, between different urls or at the end of paragraph.
                url_style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
                self.rtc.SetStyleEx(rt.RichTextRange(position, position + 1), url_style, rt.RICHTEXT_SETSTYLE_REMOVE)
                # Without moving the caret you can still type in the now incorrect url style.
                self.rtc.MoveRight(0)
                self.rtc.Invalidate()
                self.rtc.Refresh()
                self._enable_buttons()
                self._update_style_picker()
        if key_code == wx.WXK_RETURN:
            previous_par: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position - 1)
            if not previous_par.GetTextForRange(previous_par.GetRange()):
                if not isinstance(previous_par.GetChild(0), rt.RichTextField):
                    # There must not be an image in the paragraph either.
                    if paragraph_style != Strings.style_list:
                        # Reapply paragraph style on empty previous lines.
                        self._change_paragraph_style(self._stylesheet.FindStyle(Strings.style_paragraph).GetStyle(),
                                                     paragraphs_only=False, remove=False, position=position - 1)
        if key_code == wx.WXK_BACK or key_code == wx.WXK_DELETE:
            # Remove any image on any delete key and turn all potential text into the next style.
            for child in p.GetChildren():
                if isinstance(child, rt.RichTextField):
                    if len(p.GetChildren()) == 1:
                        # There is no text being appended, remove the image paragraph completely, removing just the
                        # child removes the paragraph but confuses the control.
                        self.rtc.Delete(p.GetRange())
                    else:
                        # Backspacing into the image with some text from the next paragraph, remove just the image.
                        p.RemoveChild(child, deleteChild=True)
                        self.rtc.Invalidate()
                        self.rtc.Refresh()
            if paragraph_style == Strings.style_image:
                # If backspacing into an image from a different style, the image style would survive so we have to
                # reapply the correct previous style saved in skip key method. This needs to be applied to lists too.
                if self._previous_style == Strings.style_image:
                    self._change_style(Strings.style_paragraph, force_paragraph=True)
                else:
                    self._change_style(self._previous_style, force_paragraph=True)
                    self.rtc.MoveToParagraphStart()
                self._enable_buttons()
                self.rtc.EndBatchUndo()
                return
            if key_code == wx.WXK_BACK and paragraph_style == Strings.style_list:
                # Turn a list item into paragraph if the bullet is deleted.
                attrs: rt.RichTextAttr = p.GetAttributes()
                if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                    self._change_style(Strings.style_paragraph)
                    self.rtc.EndSuppressUndo()
            if self._previous_style == Strings.style_paragraph and paragraph_style == Strings.style_paragraph:
                # Do not reapply style if the two lines are paragraphs. Prevents broken join of paragraphs where links
                # and bold text would disappear.
                print(p.GetChildren())
                self.rtc.EndBatchUndo()
                return
            if paragraph_style != Strings.style_list:
                # Reapply current paragraph style on backspace or delete to prevent mixed styles
                # (like joining heading + paragraph)
                # Does not work for list since the style is reapplied turns the removed list back into list again.
                self._change_style(paragraph_style, force_paragraph=True)
                self.rtc.MoveLeft(0)
                self.rtc.EndBatchUndo()
                return
        if self.rtc.BatchingUndo():
            self.rtc.EndBatchUndo()
        # Clear previous style once it has been used. This allows storing previous style only once in the beginning of
        # backspace/delete long press.
        self._previous_style = None
        # TODO link not restored on title to par undo
        # TODO disable bold in heading style
        # TODO selection delete does weird things

    def _on_key_down(self, event: wx.KeyEvent) -> None:
        """
        Handle key presses that should be ignored, stores last style and begins batch undo.
        :param event: Used to get key code.
        :return: None
        """
        key_code = event.GetKeyCode()
        # Disable shift enter since it is broken and does not break lines consistently.
        if key_code == wx.WXK_RETURN and event.GetModifiers() == wx.MOD_SHIFT:
            return

        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        paragraph_style, character_style = self._get_style_at_pos(position)
        # Save style before the caret moves to prevent incorrect styling after backspacing into an image.
        # Also used in paragraph joining.
        if not self._previous_style:
            self._previous_style = paragraph_style

        if key_code == wx.WXK_BACK or key_code == wx.WXK_DELETE:
            # Undo batch needs to start here, otherwise rtc manages to process delete text before the batch starts.
            if not self.rtc.BatchingUndo():
                # Prevent starting multiple batch undo actions while holding backspace/delete key. This would lead to
                # the need to press ctrl+z multiple times without seeing any change. Because you get multiple key down
                # event but only one batch finishing up event. This way the whole deleted section is undone.
                self.rtc.BeginBatchUndo(Strings.undo_last_action)

        _, next_character_style = self._get_style_at_pos(position + 1)
        if character_style == Strings.style_url and next_character_style == Strings.style_url:
            if event.GetKeyCode() == wx.WXK_RETURN:
                # Prevent return key inside url style but not at the end of the link.
                return

        if paragraph_style == Strings.style_image:
            # Prevent everything except arrows and return.
            if key_code == wx.WXK_LEFT or key_code == wx.WXK_RIGHT or key_code == wx.WXK_UP or key_code == wx.WXK_DOWN \
                    or key_code == wx.WXK_RETURN:
                if key_code == wx.WXK_RETURN:
                    # Move to the end of the paragraph and finish the new line there. New lines before image incorrectly
                    # continues the image style.
                    self.rtc.MoveToLineEnd()
                event.Skip()
            else:
                return
        else:
            event.Skip()

    def _on_key(self, event: wx.KeyEvent) -> None:
        """
        Handle key up events.
        :param event: Used to get key code.
        :return: None
        """
        print('key')
        event.Skip()
        #self._modify_text(event.GetKeyCode())

    def _text_evt_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle left mouse click. Updates GUI controls.
        :param event: Not used.
        :return: None
        """
        print('text')
        self._update_style_picker()
        self._enable_buttons()
        event.Skip()

    def _on_mouse(self, event: wx.MouseEvent) -> None:
        """
        Handle left mouse click. Updates GUI controls.
        :param event: Not used.
        :return: None
        """
        self._update_style_picker()
        self._enable_buttons()
        event.Skip()

    def _style_picker_handler(self, evt: wx.CommandEvent) -> None:
        """
        Handles style changes from the style picker list box.
        :param evt: Used to get the name of the style in stylesheet
        :return: None
        """
        self._change_style(evt.GetString())

    def _enable_buttons(self) -> None:
        """
        Enable or disable styling buttons based on caret position.
        :return: None
        """
        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        paragraph_style, character_style = self._get_style_at_pos(position)
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        if not p.GetTextForRange(p.GetRange()) and paragraph_style == Strings.style_paragraph:
            # Only allow inserting images on an empty line.
            self._image_button.Enable()
        else:
            self._image_button.Disable()
        if paragraph_style == Strings.style_image:
            self._style_picker.Disable()
            # Remove selection from the picker to avoid confusing flicker.
            self._style_picker.SetSelection(wx.NOT_FOUND)
        else:
            self._style_picker.Enable()
        if paragraph_style == Strings.style_heading_3 or paragraph_style == Strings.style_heading_4:
            url_index = self._style_picker.FindString(Strings.style_url)
            if url_index != wx.NOT_FOUND:
                self._style_picker.Delete(url_index)
        elif self._style_picker.FindString(Strings.style_url) == wx.NOT_FOUND:
            self._style_picker.Append(Strings.style_url)

    def print_current_styles(self):
        print('---')
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

    def _write_field(self, evt: wx.CommandEvent) -> None:
        """
        Write an ImageInText or Video into the text area.
        :param evt: Not used.
        :return: None
        """
        # TODO copy paste problems
        # TODO memory leak in orphaned images and link, maybe reconcile on idle.
        self.rtc.BeginBatchUndo(Strings.undo_last_action)
        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        # Set the image style.
        img_style = self._stylesheet.FindParagraphStyle(Strings.style_image).GetStyle()
        self._change_paragraph_style(img_style, paragraphs_only=False, remove=False, position=position)

        new_field = self._register_field()
        self.rtc.WriteField(new_field.GetName(), rt.RichTextProperties())
        # Return focus to the text area.
        self.rtc.EndBatchUndo()
        wx.CallLater(100, self.rtc.SetFocus)

    @staticmethod
    def _register_field() -> ImageTextField:
        """
        Register a new custom field that represent an image.
        :return: None
        """
        video = Video('test video', 534, 534, 'http://www.google.com')
        video.seo_test_self()
        field_type = ImageTextField(video)
        rt.RichTextBuffer.AddFieldType(field_type)
        return field_type

    def _insert_link(self, text: str, link_id: str, color: wx.Colour) -> None:
        """
        Insert a link into text at current position.
        :param text: The visible text.
        :param link_id: The ID of the link
        :param color: The color of the background of the link.
        :return: None
        """
        url_style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
        if color == wx.RED:
            url_style.SetBackgroundColour(wx.RED)
        else:
            url_style.SetBackgroundColour(wx.WHITE)

        self.rtc.BeginStyle(url_style)
        self.rtc.BeginURL(link_id)
        self.rtc.WriteText(text)
        self.rtc.EndURL()
        self.rtc.EndStyle()

    def _change_color(self, evt: wx.CommandEvent) -> None:
        """
        Change text color to green
        :param evt: Not used
        :return: None
        """
        attr = rt.RichTextAttr()
        r = self.rtc.GetSelectionRange()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        attr.SetTextColour(wx.Colour(234, 134, 88))
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

    def insert_sample_text(self) -> None:
        """
        Insert sample text.
        :return: None
        """
        self.rtc.BeginSuppressUndo()
        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.BeginParagraphStyle(Strings.style_heading_3)
        self.rtc.WriteText('Example H3 Heading')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.BeginParagraphStyle(Strings.style_heading_4)
        self.rtc.WriteText('Example H4 Heading')
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        self.rtc.BeginParagraphStyle(Strings.style_paragraph)
        self.rtc.WriteText('Example paragraph ')
        self._insert_link('link', '42', wx.RED)
        self.rtc.Newline()
        self.rtc.EndParagraphStyle()

        list_style = self._stylesheet.FindListStyle(Strings.style_list).GetCombinedStyleForLevel(0)
        self.rtc.BeginStyle(list_style)
        self.rtc.WriteText('Example list ')
        self._insert_link('link', '43', wx.WHITE)
        self.rtc.WriteText(' item')
        self.rtc.Newline()
        self.rtc.WriteText('Example list item')
        self.rtc.Newline()
        self.rtc.EndStyle()

        self.rtc.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
        self.rtc.Newline()

        self.rtc.LayoutContent()
        self.rtc.EndSuppressUndo()


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(700, 700), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.insert_sample_text()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
