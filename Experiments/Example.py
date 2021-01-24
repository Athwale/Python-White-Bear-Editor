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
        self._disable_input = False

        self._click_counter = 0
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_click_timer, self._timer)

        self._style_picker = wx.ListBox(self, -1, size=(100, 160))

        self.rtc.SetStyleSheet(self._stylesheet)
        self._color_button = wx.Button(self, wx.ID_FILE1, 'color 1')
        self._color_button_1 = wx.Button(self, wx.ID_FILE2, 'color 2')
        self._bold_button = wx.Button(self, -1, 'bold')
        self._image_button = wx.Button(self, -1, 'image')
        self._refresh_button = wx.Button(self, -1, 'refresh')
        self._image_button.Disable()

        self._controls_sizer.Add(self._style_picker)
        self._controls_sizer.Add(self._color_button)
        self._controls_sizer.Add(self._color_button_1)
        self._controls_sizer.Add(self._bold_button)
        self._controls_sizer.Add(self._image_button)
        self._controls_sizer.Add(self._refresh_button)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self._main_sizer.Add(self._controls_sizer)
        self.SetSizer(self._main_sizer)

        self.Bind(wx.EVT_LISTBOX, self._style_picker_handler, self._style_picker)
        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button)
        self.Bind(wx.EVT_BUTTON, self._change_color, self._color_button_1)
        self.Bind(wx.EVT_BUTTON, self._change_bold, self._bold_button)
        self.Bind(wx.EVT_BUTTON, self._write_field, self._image_button)
        self.Bind(wx.EVT_BUTTON, self._refresh, self._refresh_button)

        self.rtc.Bind(wx.EVT_LEFT_UP, self._on_mouse_left)
        # Updates style picker in times mouse is not registered.
        self.rtc.Bind(wx.EVT_IDLE, self._update_gui_handler)

        self.rtc.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.rtc.Bind(wx.EVT_KEY_UP, self._update_gui_handler)
        self.rtc.Bind(wx.EVT_MENU, self._prevent_paste, id=wx.ID_PASTE)
        self.rtc.Bind(wx.EVT_MENU, self._undo_redo, id=wx.ID_UNDO)
        self.rtc.Bind(wx.EVT_MENU, self._undo_redo, id=wx.ID_REDO)

        self.rtc.GetBuffer().CleanUpFieldTypes()
        # Disable drag and drop text.
        self.rtc.SetDropTarget(None)

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
        # Do not se specific font color, color is retained in each text object.
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
        stl_heading_4.SetFontSize(Numbers.heading_4_size)
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
        stl_link.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_link.SetCharacterStyleName(Strings.style_url)
        stl_link.SetFontFaceName(Strings.style_url)
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
        self._style_picker.InsertItems(names, 0)

    def _change_style(self, style_name: str, position: int) -> None:
        """
        Changes the style of the current paragraph or selection.
        :param style_name: The name of a style in stylesheet.
        :param position: The position of the caret. This is needed because when changing style over multiple paragraphs
        the position is passed from selection.
        This is used when joining heading and ordinary paragraph using delete or backspace.
        :return: None
        """
        if position == -1:
            position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())

        if style_name == Strings.style_heading_3 or style_name == Strings.style_heading_4:
            self._apply_heading_style(style_name, position)

        elif style_name == Strings.style_paragraph:
            self._apply_paragraph_style(position)

        elif style_name == Strings.style_list:
            self._apply_list_style(position)

        elif style_name == Strings.style_url:
            self._apply_url_style()

        # Unless we simulate a move, you can still type in the wrong style after change.
        self.rtc.Invalidate()
        self.rtc.Refresh()
        self.rtc.MoveRight(0)
        self._update_style_picker()

    def _apply_heading_style(self, heading_type: str, position: int) -> None:
        """
        Changes current paragraph under the cursor into a heading 3 or 4, removing any links.
        :param heading_type: The heading style size.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        style: rt.RichTextAttr = self._stylesheet.FindStyle(heading_type).GetStyle()
        p_range = p.GetRange().FromInternal()
        # Save text children attributes to restore them after forcing the paragraph style.
        # We need text weight, color, background, underline. URL flag remains untouched. Font size will be replaced by
        # the heading style.
        child_list = []
        for child in p.GetChildren():
            saved_attrs = {}
            # The built in wx Copy method causes the children to disappear for a wtf reason.
            # We only need to preserve font color, the rest will be set by the heading style.
            attrs: rt.RichTextAttr = child.GetAttributes()
            saved_attrs['color'] = attrs.GetTextColour()
            child_list.append(saved_attrs)

        # Brute force the paragraph into the heading style paragraph attributes are reset completely which removes list
        # style. Character attributes are changed but not reset. Specific attributes are then changed separately.
        end_batch = False
        if not self.rtc.BatchingUndo():
            # Only batch undo if we are not already recording changes from the beginning of modify text method.
            # Basically only if this method is called from the style picker.
            self.rtc.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.rtc.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                                  | rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            self.rtc.EndBatchUndo()

        # The paragraph changes after style set, so find it again.
        p = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        # Restore and set only relevant attributes for the style.
        for child, attr_dict in zip(p.GetChildren(), child_list):
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontSize(style.GetFontSize())
            attrs.SetFontWeight(wx.FONTWEIGHT_BOLD)
            attrs.SetBackgroundColour(style.GetBackgroundColour())
            attrs.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore())
            attrs.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter())
            attrs.SetFontFaceName(style.GetFontFaceName())
            attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            # Only links can be underlined, it is safe to remove it here.
            attrs.SetFontUnderlined(style.GetFontUnderlined())
            if attrs.HasURL():
                # TODO try save, this might still appear in xml if we use it. How is other url remove going to work?
                # If any child has a url flag, remove it and set font color to normal.
                attrs.SetURL('')
                attrs.SetFlags(attrs.GetFlags() ^ wx.TEXT_ATTR_URL)
                attrs.SetTextColour(style.GetTextColour())
                attrs.SetCharacterStyleName('')

    def _apply_paragraph_style(self, position: int) -> None:
        """
        Changes current paragraph under the cursor into the paragraph style defined for normal text.
        Retains links, text weight and color.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        # This is needed to prevent loss of children attributes when typing quickly for some reason.
        p.Defragment(rt.RichTextDrawingContext(p.GetBuffer()))
        style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_paragraph).GetStyle()
        p_range = p.GetRange().FromInternal()
        child_list = []
        for child in p.GetChildren():
            saved_attrs = {}
            attrs: rt.RichTextAttr = child.GetAttributes()
            if attrs.GetFontFaceName() == Strings.style_heading_3 or attrs.GetFontFaceName() == Strings.style_heading_4:
                # Do not save bold font weight from heading style we assume the weight should be normal.
                saved_attrs['weight'] = wx.FONTWEIGHT_NORMAL
            else:
                saved_attrs['weight'] = attrs.GetFontWeight()
            # Font color does not need to be saved, it is preserved from the previous child. Background is for urls.
            saved_attrs['background'] = attrs.GetBackgroundColour()
            child_list.append(saved_attrs)

        end_batch = False
        if not self.rtc.BatchingUndo():
            self.rtc.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.rtc.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                                  | rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            self.rtc.EndBatchUndo()

        p = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        for child, attr_dict in zip(p.GetChildren(), child_list):
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontWeight(attr_dict['weight'])
            attrs.SetBackgroundColour(style.GetBackgroundColour())
            attrs.SetFontSize(style.GetFontSize())
            attrs.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore())
            attrs.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter())
            attrs.SetFontFaceName(Strings.style_paragraph)
            attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            if attrs.HasURL():
                # Only urls have background color and underline.
                attrs.SetBackgroundColour(attr_dict['background'])
                attrs.SetFontUnderlined(True)
                attrs.SetFontFaceName(Strings.style_url)

    def _apply_list_style(self, position: int) -> None:
        """
        Changes paragraph on position into list item.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        p.Defragment(rt.RichTextDrawingContext(p.GetBuffer()))
        style_def: rt.RichTextListStyleDefinition = self._stylesheet.FindStyle(Strings.style_list)
        style: rt.RichTextAttr = style_def.GetStyle()
        p_range = p.GetRange().FromInternal()
        child_list = []
        for child in p.GetChildren():
            child: rt.RichTextPlainText
            saved_attrs = {}
            # The build in wx Copy method causes the children to disappear for a wtf reason.
            attrs: rt.RichTextAttr = child.GetAttributes()
            if attrs.GetFontFaceName() == Strings.style_heading_3 or attrs.GetFontFaceName() == Strings.style_heading_4:
                # Do not save bold font weight from heading style.
                saved_attrs['weight'] = wx.FONTWEIGHT_NORMAL
            else:
                saved_attrs['weight'] = attrs.GetFontWeight()
            # Font color does not need to be saved, it is preserved from the previous child.
            saved_attrs['background'] = attrs.GetBackgroundColour()
            child_list.append(saved_attrs)

        end_batch = False
        if not self.rtc.BatchingUndo():
            self.rtc.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.rtc.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                                  | rt.RICHTEXT_SETSTYLE_RESET)
        self.rtc.SetListStyle(p_range, style_def, specifiedLevel=0, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO
                                                                          | rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL)
        if end_batch:
            self.rtc.EndBatchUndo()

        p = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        # Restore only relevant attributes to the new children. The order is the same.
        for child, attr_dict in zip(p.GetChildren(), child_list):
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontWeight(attr_dict['weight'])
            attrs.SetFontSize(style.GetFontSize())
            attrs.SetBackgroundColour(style.GetBackgroundColour())
            attrs.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore())
            attrs.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter())
            attrs.SetFontFaceName(Strings.style_list)
            attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            if attrs.HasURL():
                attrs.SetBackgroundColour(attr_dict['background'])
                attrs.SetFontUnderlined(True)
                attrs.SetFontFaceName(Strings.style_url)

    def _apply_url_style(self) -> None:
        """
        Changes current selection the url character style.
        :return: None
        """
        if self.rtc.HasSelection():
            link_range = self.rtc.GetSelectionRange()
            self.rtc.SetStyleEx(link_range, self._stylesheet.FindStyle(Strings.style_url).GetStyle(),
                                flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)

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

    def _modify_text(self) -> None:
        """
        Handle keypress events. Runs on key down.
        :return: None
        """
        # Disable other keyboard input while this method is working?
        self._disable_input = True

        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        paragraph_style, character_style = self._get_style_at_pos(position)

        # End url style if next character has different or no url.
        if character_style == Strings.style_url:
            style_carrier = rt.RichTextAttr()
            self.rtc.GetStyle(position, style_carrier)
            current_url = style_carrier.GetURL()
            self.rtc.GetStyle(position + 1, style_carrier)
            next_url = style_carrier.GetURL()
            if not next_url or current_url != next_url or position == (p.GetRange()[1] - 1):
                # End url style if we are at th end of a url, between different urls or at the end of paragraph.
                url_style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
                if p.GetTextForRange(rt.RichTextRange(position, position)) == ' ':
                    # Stop the url style on blank space
                    self.rtc.SetStyleEx(rt.RichTextRange(position, position + 1), url_style,
                                        rt.RICHTEXT_SETSTYLE_REMOVE)
                # Without moving the caret you can still type in the now incorrect url style.
                self.rtc.MoveRight(0)

        # Turn a list item into paragraph if the bullet is deleted. Must be here because bullet delete is not considered
        # a text event. The order here is important, this must be before mixed style fix.
        if paragraph_style == Strings.style_list:
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                self._change_style(Strings.style_paragraph, position=-1)
                paragraph_style = Strings.style_paragraph
                p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        # Turn empty lines into paragraph style. Also turns deleted images into paragraph style.
        elif not p.GetTextForRange(p.GetRange()):
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                if not isinstance(p.GetChild(0), rt.RichTextField):
                    # Field is not seen as text.
                    self._change_style(Strings.style_paragraph, position=-1)
                    # Changing the style above also changes the paragraph address in memory, find it again then.
                    # Not doing this may cause segfaults.
                    p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)

        #  Prevent images in other styles
        if len(p.GetChildren()) > 1:
            # Two things can happen. Image is the first child, delete it.
            if isinstance(p.GetChild(0), rt.RichTextField):
                # We can not delete the child directly, it confuses the paragraphs.
                self.rtc.Delete(rt.RichTextRange(p.GetRange()[0], p.GetRange()[0] + 1))
                # Change the style of the new image-less paragraph to the correct next style.
                font_face = p.GetChild(0).GetAttributes().GetFontFaceName()
                if font_face == Strings.style_url:
                    # We do not want to change whole paragraphs into links, so use paragraph.
                    font_face = Strings.style_paragraph
                self._change_style(font_face, position=-1)
                # Changing the style above also changes the paragraph address in memory, find it again then.
                p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
            else:
                # Image is not the first child, find it and delete it.
                for child in p.GetChildren():
                    if isinstance(child, rt.RichTextField):
                        self.rtc.Delete(rt.RichTextRange(child.GetRange()[0], child.GetRange()[1] + 1))

        # Prevent mixed styles using child based approach.
        if not isinstance(p.GetChild(0), rt.RichTextField):
            # The style of the first paragraph child.
            first_style: str = p.GetChild(0).GetAttributes().GetFontFaceName()
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() == wx.TEXT_ATTR_BULLET_STYLE_STANDARD and not first_style:
                # Empty list line has no child and no first style.
                first_style = Strings.style_list
            if first_style == Strings.style_url:
                first_style = paragraph_style
            self._change_style(first_style, position=-1)

        self._update_style_picker()
        self._enable_buttons()

        if self.rtc.BatchingUndo():
            self.rtc.EndBatchUndo()

        self._disable_input = False

    def _on_key_down(self, event: wx.KeyEvent) -> None:
        """
        Handle key presses that should be ignored, stores last style and begins batch undo.
        :param event: Used to get key code.
        :return: None
        """
        if self._disable_input:
            return

        key_code = event.GetKeyCode()
        # Disable shift enter since it is broken and does not break lines consistently.
        if key_code == wx.WXK_RETURN and event.GetModifiers() == wx.MOD_SHIFT:
            return

        # Do not run this method when we pressed ctrl. Events for ctrl-z are EVT_MENU.
        if event.ControlDown():
            return

        if not self.rtc.BatchingUndo():
            # Start batch here because delete text would go through before the batch would be started in modify text.
            self.rtc.BeginBatchUndo(Strings.undo_last_action)

        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        paragraph_style, character_style = self._get_style_at_pos(position)

        _, next_character_style = self._get_style_at_pos(position + 1)
        if character_style == Strings.style_url and next_character_style == Strings.style_url:
            if event.GetKeyCode() == wx.WXK_RETURN:
                # Prevent return key inside url style but not at the end of the link.
                return

        if paragraph_style == Strings.style_image:
            # Prevent everything except arrows, return and erase keys.
            if key_code == wx.WXK_LEFT or key_code == wx.WXK_RIGHT or key_code == wx.WXK_UP or key_code == wx.WXK_DOWN \
                    or key_code == wx.WXK_RETURN or key_code == wx.WXK_BACK or key_code == wx.WXK_DELETE:
                if key_code == wx.WXK_RETURN:
                    # Move to the end of the paragraph and finish the new line there. New lines before image incorrectly
                    # continues the image style.
                    self.rtc.MoveToLineEnd()
                event.Skip()
            else:
                return
        else:
            event.Skip()
        # Calls the function when the current event handler has exited. wx.TEXT_EVT can not be used because it does not
        # fire on list bullet deletion.
        wx.CallAfter(self._modify_text)

    def _prevent_paste(self, event: wx.CommandEvent) -> None:
        """
        Prevent paste if we are in an image style.
        :param event: Used to get id.
        :return: None
        """
        if event.GetId() == wx.ID_PASTE:
            if not self.rtc.BatchingUndo():
                # We get here without starting undo batch, since on key down ignores ctrl.
                self.rtc.BeginBatchUndo(Strings.undo_last_action)
            position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
            paragraph_style, _ = self._get_style_at_pos(position)
            if paragraph_style == Strings.style_image:
                return
            self._modify_text()
        event.Skip()

    def _undo_redo(self, event: wx.CommandEvent):
        processor: wx.CommandProcessor = self.rtc.GetCommandProcessor()
        if processor.GetCurrentCommand():
            # There may be no command.
            if event.GetId() == wx.ID_UNDO:
                if processor.GetCurrentCommand().GetName() == 'Paste':
                    # Paste is followed by style change, we want to undo both in one go.
                    processor.Undo()
                    processor.Undo()
                else:
                    processor.Undo()
            elif event.GetId() == wx.ID_REDO:
                if processor.GetCurrentCommand().GetName() == 'Paste':
                    # Paste is followed by style change, we want to undo both in one go.
                    processor.Redo()
                    processor.Redo()
                else:
                    processor.Redo()
        self.rtc.MoveRight(0)

    def _update_gui_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle key events to update GUI controls.
        :param event: Not used.
        :return: None
        """
        self._update_style_picker()
        self._enable_buttons()
        event.Skip()

    def _on_mouse_left(self, event: wx.MouseEvent) -> None:
        """
        Handle left mouse click. Starts a timer and counts left mouse clicks in order to allow three click select.
        :param event: Not used.
        :return: None
        """
        if not self._timer.IsRunning():
            self._timer.Start(Numbers.three_click_timeout)
        self._click_counter = self._click_counter + 1
        event.Skip()

    def _on_click_timer(self, event) -> None:
        """
        When the timer runs out and if three left click were made, select whole current paragraph.
        :param event: Not used.
        :return: None
        """
        if self._click_counter >= 3:
            position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
            p_range: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position).GetRange()
            self.rtc.SetSelectionRange(p_range)
        self._click_counter = 0
        self._timer.Stop()

    def _style_picker_handler(self, evt: wx.CommandEvent) -> None:
        """
        Handles style changes from the style picker list box.
        :param evt: Used to get the name of the style in stylesheet
        :return: None
        """
        if not self.rtc.BatchingUndo():
            self.rtc.BeginBatchUndo(Strings.undo_last_action)
        if self.rtc.HasSelection():
            selection_range = self.rtc.GetSelectionRange()
            for position in range(selection_range[0], selection_range[1] + 1):
                # Get the different paragraphs in the selection
                p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
                if p and not isinstance(p.GetChild(0), rt.RichTextField):
                    # Skip changing style on images
                    if p.GetAttributes().GetFontFaceName() != evt.GetString():
                        # Apply style to all the paragraphs unless they are already in the style
                        self._change_style(evt.GetString(), position)
        else:
            self._change_style(evt.GetString(), position=-1)
        self.rtc.EndBatchUndo()

    def _enable_buttons(self) -> None:
        """
        Enable or disable styling buttons based on caret position.
        :return: None
        """
        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        paragraph_style, character_style = self._get_style_at_pos(position)
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        if not p.GetTextForRange(p.GetRange()) and paragraph_style == Strings.style_paragraph \
                and not isinstance(p.GetChild(0), rt.RichTextField):
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

        if not self.rtc.HasSelection():
            # Disable url style unless we have a selection.
            url_index = self._style_picker.FindString(Strings.style_url)
            if url_index != wx.NOT_FOUND:
                self._style_picker.Delete(url_index)
        if paragraph_style == Strings.style_heading_3 or paragraph_style == Strings.style_heading_4:
            # Disable url option in headings.
            url_index = self._style_picker.FindString(Strings.style_url)
            if url_index != wx.NOT_FOUND:
                self._style_picker.Delete(url_index)
        elif self.rtc.HasSelection():
            selection_range = self.rtc.GetSelectionRange()
            paragraphs = set()
            for position in range(selection_range[0], selection_range[1] + 1):
                # Get the different paragraphs in the selection
                paragraphs.add(self.rtc.GetFocusObject().GetParagraphAtPosition(position))
            if len(paragraphs) == 1:
                if self._style_picker.FindString(Strings.style_url) == wx.NOT_FOUND:
                    self._style_picker.Append(Strings.style_url)
            else:
                url_index = self._style_picker.FindString(Strings.style_url)
                if url_index != wx.NOT_FOUND:
                    self._style_picker.Delete(url_index)

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
        self._image_button.Disable()
        self._write_image(from_button=True)
        # TODO memory leak in orphaned images and link, maybe reconcile on idle.
        # Return focus to the text area.
        wx.CallLater(100, self.rtc.SetFocus)

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
        if evt.GetId() == wx.ID_FILE1:
            color = wx.Colour(234, 134, 88)
        else:
            color = wx.Colour(124, 144, 25)
        if self.rtc.HasSelection():
            self.rtc.BeginBatchUndo(Strings.undo_bold)
            color_range = self.rtc.GetSelectionRange()
            for char in range(color_range[0], color_range[1]):
                if char + 1 > color_range[1] + 1:
                    break
                single_range = rt.RichTextRange(char, char + 1)
                # Get the attributes of the single char range and modify them in place. Otherwise changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self.rtc.GetStyleForRange(single_range, attr)
                # Ignore links.
                if attr.HasURL():
                    continue
                attr.SetTextColour(color)
                self.rtc.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
            self.rtc.EndBatchUndo()
        else:
            self.rtc.BeginTextColour(color)

    def _change_bold(self, evt: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        if self.rtc.HasSelection():
            self.rtc.BeginBatchUndo(Strings.undo_bold)
            self.rtc.BeginBold()
            bold_range = self.rtc.GetSelectionRange()
            for char in range(bold_range[0], bold_range[1]):
                if char + 1 > bold_range[1] + 1:
                    break
                single_range = rt.RichTextRange(char, char + 1)
                # Get the attributes of the single char range and modify them in place. Otherwise changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self.rtc.GetStyleForRange(single_range, attr)
                font_face = attr.GetFontFaceName()
                # Ignore links and headings.
                if font_face == Strings.style_heading_3 or font_face == Strings.style_heading_4 or \
                        font_face == Strings.style_image:
                    continue
                if attr.HasURL():
                    continue
                # Switch bold to normal and normal to bold.
                if attr.GetFontWeight() == wx.FONTWEIGHT_NORMAL:
                    attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
                else:
                    attr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
                self.rtc.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
            self.rtc.EndBatchUndo()
        else:
            if not self.rtc.IsSelectionBold():
                self.rtc.BeginBold()
            else:
                self.rtc.EndBold()

    def _write_image(self, from_button: bool) -> None:
        """
        Write an ImageInText or Video into the text area.
        :param from_button: Must be True if the insert is made from GUI.
        :return: None
        """
        new_field = self._register_field()
        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        buffer: rt.RichTextBuffer = self.rtc.GetFocusObject()

        style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_image).GetStyle()
        p: rt.RichTextParagraph = self.rtc.GetFocusObject().GetParagraphAtPosition(position)
        p_range = p.GetRange().FromInternal()

        self.rtc.BeginBatchUndo(Strings.undo_last_action)
        if from_button:
            self.rtc.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_RESET)
        buffer.InsertFieldWithUndo(self.rtc.GetBuffer(), position, new_field.GetName(), rt.RichTextProperties(),
                                   self.rtc, rt.RICHTEXT_INSERT_NONE, rt.RichTextAttr())
        self.rtc.EndBatchUndo()

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

        self.rtc.BeginStyle(self._stylesheet.FindStyle(Strings.style_image).GetStyle())
        self._write_image(from_button=False)
        self.rtc.Newline()
        self.rtc.EndStyle()

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
        self._change_style(Strings.style_paragraph, position=-1)

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
