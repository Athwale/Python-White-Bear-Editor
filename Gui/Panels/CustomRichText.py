import wx
import wx.richtext as rt

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.EditLinkDialog import EditLinkDialog
from Tools.Document.ArticleElements.Heading import Heading
from Tools.Document.ArticleElements.ImageInText import ImageInText
from Tools.Document.ArticleElements.Link import Link
from Tools.Document.ArticleElements.Paragraph import Paragraph
from Tools.Document.ArticleElements.Text import Text, Break
from Tools.Document.ArticleElements.UnorderedList import UnorderedList
from Tools.Document.ArticleElements.Video import Video
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.ImageTextField import ImageTextField


class CustomRichText(rt.RichTextCtrl):
    """
    Custom rich text control
    """

    def __init__(self, img_tool_id: int, video_tool_id: int, style_control: wx.ListBox, parent, style):
        """
        Constructor for the custom rich text control.
        :param img_tool_id: Id of the insert image tool.
        :param video_tool_id: Id of the insert video tool.
        :param style_control: Style control from gui.
        :param parent: Parent of this control.
        :param style: wx style attributes.
        """
        super().__init__(parent, -1, style=style)
        self._parent = parent
        self._document = None
        self.img_tool_id = img_tool_id
        self.video_tool_id = video_tool_id
        # Used to prevent over-calling methods on keypress.
        self._disable_input = False
        self._click_counter = 0

        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')
        self.SetStyleSheet(self._stylesheet)

        self._style_picker = style_control

        # Used for three click select.
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_click_timer, self._timer)

        self._main_frame = wx.GetTopLevelParent(self)
        self.Bind(wx.EVT_LISTBOX, self._style_picker_handler, self._style_picker)
        self.Bind(wx.EVT_TEXT_URL, self.url_in_text_click_handler, self)
        self.Bind(wx.EVT_MENU, self.on_insert_image, self._main_frame.insert_img_tool)
        self.Bind(wx.EVT_MENU, self.on_insert_image, self._main_frame.insert_img_tool)
        self.Bind(wx.EVT_MENU, self._change_bold, self._main_frame.bold_tool)

        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left)
        self.Bind(wx.EVT_MOTION, self._update_gui_handler)
        self.Bind(wx.EVT_LEFT_UP, self._update_gui_handler)

        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_KEY_UP, self._update_gui_handler)
        self.Bind(wx.EVT_MENU, self._prevent_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self._undo_redo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self._undo_redo, id=wx.ID_REDO)

        # Disable drag and drop text.
        self.SetDropTarget(None)
        self._default_style: rt.RichTextAttr = self.GetDefaultStyleEx()

        self._add_text_handlers()
        self._create_styles()
        self._fill_style_picker()

    @staticmethod
    def _add_text_handlers() -> None:
        """
        Add handler to the main text area rich text control to be able to save in xml and remove plain text handler.
        :return: None
        """
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="XML", ext="xml", type=99))
        rt.RichTextBuffer.RemoveHandler('Text')

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

        self.SetStyleSheet(self._stylesheet)

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
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())

        if style_name == Strings.style_heading_3 or style_name == Strings.style_heading_4:
            self._apply_heading_style(style_name, position)

        elif style_name == Strings.style_paragraph:
            self._apply_paragraph_style(position)

        elif style_name == Strings.style_list:
            self._apply_list_style(position)

        elif style_name == Strings.style_url:
            self._apply_url_style()

        # Unless we simulate a move, you can still type in the wrong style after change.
        self.Invalidate()
        self.Refresh()
        self.MoveRight(0)
        self._update_style_picker()

    def _apply_heading_style(self, heading_type: str, position: int) -> None:
        """
        Changes current paragraph under the cursor into a heading 3 or 4, removing any links.
        :param heading_type: The heading style size.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
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
        if not self.BatchingUndo():
            # Only batch undo if we are not already recording changes from the beginning of modify text method.
            # Basically only if this method is called from the style picker.
            self.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                              | rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            self.EndBatchUndo()

        # The paragraph changes after style set, so find it again.
        p = self.GetFocusObject().GetParagraphAtPosition(position)
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
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
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
        if not self.BatchingUndo():
            self.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                              | rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            self.EndBatchUndo()

        p = self.GetFocusObject().GetParagraphAtPosition(position)
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
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
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
        if not self.BatchingUndo():
            self.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        self.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY
                                              | rt.RICHTEXT_SETSTYLE_RESET)
        self.SetListStyle(p_range, style_def, specifiedLevel=0, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO
                                                                      | rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL)
        if end_batch:
            self.EndBatchUndo()

        p = self.GetFocusObject().GetParagraphAtPosition(position)
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
        if self.HasSelection():
            link_range = self.GetSelectionRange()
            self.SetStyleEx(link_range, self._stylesheet.FindStyle(Strings.style_url).GetStyle(),
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
        self.GetStyle(position, style_carrier)
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
        paragraph_style_name, character_style_name = self._get_style_at_pos(self.GetAdjustedCaretPosition
                                                                            (self.GetCaretPosition()))
        if character_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(character_style_name))
        elif paragraph_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(paragraph_style_name))
        # Return focus back into the text area. The focus must happen a little later when the style picker is finished.
        wx.CallLater(100, self.SetFocus)

    def _modify_text(self) -> None:
        """
        Handle keypress events. Runs on key down.
        :return: None
        """
        # Disable other keyboard input while this method is working?
        self._disable_input = True

        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        paragraph_style, character_style = self._get_style_at_pos(position)

        # End url style if next character has different or no url.
        if character_style == Strings.style_url:
            style_carrier = rt.RichTextAttr()
            self.GetStyle(position, style_carrier)
            current_url = style_carrier.GetURL()
            self.GetStyle(position + 1, style_carrier)
            next_url = style_carrier.GetURL()
            if not next_url or current_url != next_url or position == (p.GetRange()[1] - 1):
                # End url style if we are at th end of a url, between different urls or at the end of paragraph.
                url_style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
                if p.GetTextForRange(rt.RichTextRange(position, position)) == ' ':
                    # Stop the url style on blank space
                    self.SetStyleEx(rt.RichTextRange(position, position + 1), url_style,
                                    rt.RICHTEXT_SETSTYLE_REMOVE)
                # Without moving the caret you can still type in the now incorrect url style.
                self.MoveRight(0)

        # Turn a list item into paragraph if the bullet is deleted. Must be here because bullet delete is not considered
        # a text event. The order here is important, this must be before mixed style fix.
        if paragraph_style == Strings.style_list:
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                self._change_style(Strings.style_paragraph, position=-1)
                paragraph_style = Strings.style_paragraph
                p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        # Turn empty lines into paragraph style. Also turns deleted images into paragraph style.
        elif not p.GetTextForRange(p.GetRange()):
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                if not isinstance(p.GetChild(0), rt.RichTextField):
                    # Field is not seen as text.
                    self._change_style(Strings.style_paragraph, position=-1)
                    # Changing the style above also changes the paragraph address in memory, find it again then.
                    # Not doing this may cause segfaults.
                    p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)

        #  Prevent images in other styles
        if len(p.GetChildren()) > 1:
            # Two things can happen. Image is the first child, delete it.
            if isinstance(p.GetChild(0), rt.RichTextField):
                # We can not delete the child directly, it confuses the paragraphs.
                self.Delete(rt.RichTextRange(p.GetRange()[0], p.GetRange()[0] + 1))
                # Change the style of the new image-less paragraph to the correct next style.
                font_face = p.GetChild(0).GetAttributes().GetFontFaceName()
                if font_face == Strings.style_url:
                    # We do not want to change whole paragraphs into links, so use paragraph.
                    font_face = Strings.style_paragraph
                self._change_style(font_face, position=-1)
                # Changing the style above also changes the paragraph address in memory, find it again then.
                p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
            else:
                # Image is not the first child, find it and delete it.
                for child in p.GetChildren():
                    if isinstance(child, rt.RichTextField):
                        self.Delete(rt.RichTextRange(child.GetRange()[0], child.GetRange()[1] + 1))

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

        if self.BatchingUndo():
            self.EndBatchUndo()

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

        if not self.BatchingUndo():
            # Start batch here because delete text would go through before the batch would be started in modify text.
            self.BeginBatchUndo(Strings.undo_last_action)

        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
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
                    self.MoveToLineEnd()
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
            if not self.BatchingUndo():
                # We get here without starting undo batch, since on key down ignores ctrl.
                self.BeginBatchUndo(Strings.undo_last_action)
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
            paragraph_style, _ = self._get_style_at_pos(position)
            if paragraph_style == Strings.style_image:
                return
            self._modify_text()
        event.Skip()

    def _undo_redo(self, event: wx.CommandEvent):
        processor: wx.CommandProcessor = self.GetCommandProcessor()
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
        self.MoveRight(0)

    def _update_gui_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle key events to update GUI controls.
        :param event: Not used.
        :return: None
        """
        if self.HasFocus():
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
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
            p_range: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position).GetRange()
            self.SetSelectionRange(p_range)
        self._click_counter = 0
        self._timer.Stop()

    def _style_picker_handler(self, evt: wx.CommandEvent) -> None:
        """
        Handles style changes from the style picker list box.
        :param evt: Used to get the name of the style in stylesheet
        :return: None
        """
        if not self.BatchingUndo():
            self.BeginBatchUndo(Strings.undo_last_action)
        if self.HasSelection():
            selection_range = self.GetSelectionRange()
            for position in range(selection_range[0], selection_range[1] + 1):
                # Get the different paragraphs in the selection
                p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
                if p and not isinstance(p.GetChild(0), rt.RichTextField):
                    # Skip changing style on images
                    if p.GetAttributes().GetFontFaceName() != evt.GetString():
                        # Apply style to all the paragraphs unless they are already in the style
                        self._change_style(evt.GetString(), position)
        else:
            self._change_style(evt.GetString(), position=-1)
        self.EndBatchUndo()

    def _enable_buttons(self) -> None:
        """
        Enable or disable styling buttons based on caret position.
        :return: None
        """
        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        paragraph_style, character_style = self._get_style_at_pos(position)
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        if not p.GetTextForRange(p.GetRange()) and paragraph_style == Strings.style_paragraph \
                and not isinstance(p.GetChild(0), rt.RichTextField):
            # Only allow inserting images on an empty paragraph line with no other images.
            self._main_frame.tool_bar.EnableTool(self.img_tool_id, True)
            self._main_frame.tool_bar.EnableTool(self.video_tool_id, True)
        else:
            self._main_frame.tool_bar.EnableTool(self.img_tool_id, False)
            self._main_frame.tool_bar.EnableTool(self.video_tool_id, False)
        if paragraph_style == Strings.style_image:
            self._style_picker.Disable()
            # Remove selection from the picker to avoid confusing flicker.
            self._style_picker.SetSelection(wx.NOT_FOUND)
        else:
            self._style_picker.Enable()

        if not self.HasSelection():
            # Disable url style unless we have a selection.
            url_index = self._style_picker.FindString(Strings.style_url)
            if url_index != wx.NOT_FOUND:
                self._style_picker.Delete(url_index)
        if paragraph_style == Strings.style_heading_3 or paragraph_style == Strings.style_heading_4:
            # Disable url option in headings.
            url_index = self._style_picker.FindString(Strings.style_url)
            if url_index != wx.NOT_FOUND:
                self._style_picker.Delete(url_index)
        elif self.HasSelection():
            selection_range = self.GetSelectionRange()
            paragraphs = set()
            for position in range(selection_range[0], selection_range[1] + 1):
                # Get the different paragraphs in the selection
                paragraphs.add(self.GetFocusObject().GetParagraphAtPosition(position))
            if len(paragraphs) == 1:
                if self._style_picker.FindString(Strings.style_url) == wx.NOT_FOUND:
                    self._style_picker.Append(Strings.style_url)
            else:
                url_index = self._style_picker.FindString(Strings.style_url)
                if url_index != wx.NOT_FOUND:
                    self._style_picker.Delete(url_index)

    def clear_self(self) -> None:
        """
        Clears all styles and prepares the control for a new article.
        :return: None
        """
        # Ensure we always end with a consistent paragraph style, this is needed because for some reason the last style
        # survives clearing.
        self.BeginParagraphStyle(Strings.style_paragraph)
        self.WriteText(' ')
        self.EndParagraphStyle()
        self._modify_text()
        self.Clear()
        self.GetBuffer().CleanUpFieldTypes()

        self.SetStyleEx(rt.RichTextRange(0, 1), self._stylesheet.FindParagraphStyle(Strings.style_paragraph).GetStyle(),
                        flags=rt.RICHTEXT_SETSTYLE_REMOVE)
        # List for some reason does not get replaced by paragraph above.
        self.SetStyleEx(rt.RichTextRange(0, 1), self._stylesheet.FindListStyle(Strings.style_list).GetStyle(),
                        flags=rt.RICHTEXT_SETSTYLE_REMOVE)

    def set_content(self, doc: WhitebearDocumentArticle) -> None:
        """
        Set the document this text area is displaying.
        :param doc: The white bear article.
        :return: None
        """
        self._document = doc
        self.BeginSuppressUndo()
        self.clear_self()

        last_was_paragraph = False
        for element in doc.get_main_text_elements():
            if isinstance(element, Paragraph):
                if last_was_paragraph:
                    # Empty paragraph substitutes shift-enter line break.
                    self.BeginParagraphStyle(Strings.style_paragraph)
                    self.WriteText('')
                    self.EndParagraphStyle()
                self._write_paragraph(element)
                last_was_paragraph = True
            elif isinstance(element, Heading):
                last_was_paragraph = False
                self._write_heading(element)
            elif isinstance(element, ImageInText):
                last_was_paragraph = False
                self._write_image(element)
            elif isinstance(element, UnorderedList):
                last_was_paragraph = False
                self._write_list(element)
            elif isinstance(element, Video):
                last_was_paragraph = False
                self._write_image(element)

        self.LayoutContent()
        self.EndSuppressUndo()
        self._modify_text()

    def _write_list(self, ul: UnorderedList) -> None:
        """
        Write an UnorderedList into the text area.
        :param ul: The list that will be on the field.
        :return: None
        """
        list_style = self._stylesheet.FindListStyle(Strings.style_list).GetCombinedStyleForLevel(0)
        self.BeginStyle(list_style)
        for li in ul.get_paragraphs():
            for element in li.get_elements():
                self._write_text(element)
            self.Newline()
        self.EndStyle()

    def _write_image(self, element) -> None:
        """
        Write an ImageInText or Video into the text area.
        :param element: The Video or ImageInText instance.
        :return: None
        """
        self.BeginStyle(self._stylesheet.FindStyle(Strings.style_image).GetStyle())
        self._write_field(element, from_button=False)
        # This new line is written as \n because otherwise the style does not end correctly at the end of page.
        self.WriteText('\n')
        self.EndStyle()

    def _write_field(self, element, from_button: bool) -> None:
        """
        Write an ImageInText or Video into the text area.
        :param from_button: Must be True if the insert is made from GUI.
        :return: None
        """
        new_field = self._register_field(element)
        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        buffer: rt.RichTextBuffer = self.GetFocusObject()

        style: rt.RichTextAttr = self._stylesheet.FindStyle(Strings.style_image).GetStyle()
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        p_range = p.GetRange().FromInternal()

        self.BeginBatchUndo(Strings.undo_last_action)
        if from_button:
            self.SetStyleEx(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_RESET)
        buffer.InsertFieldWithUndo(self.GetBuffer(), position, new_field.GetName(), rt.RichTextProperties(),
                                   self, rt.RICHTEXT_INSERT_NONE, rt.RichTextAttr())
        self.EndBatchUndo()

    def _register_field(self, element) -> ImageTextField:
        """
        Register a new custom field that represent an image.
        :param element: The Video or ImageInText to display.
        :return: None
        """
        field_type = ImageTextField(element, self._document.get_working_directory())
        rt.RichTextBuffer.AddFieldType(field_type)
        return field_type

    def _write_heading(self, h: Heading) -> None:
        """
        Write a Heading into the text area.
        :param h: A Heading instance.
        :return: None
        """
        if h.get_size() == Heading.SIZE_H3:
            style = Strings.style_heading_3
        else:
            style = Strings.style_heading_4
        self.BeginParagraphStyle(style)
        self._write_text(h.get_text())
        self.Newline()
        self.EndParagraphStyle()

    def _write_paragraph(self, p: Paragraph) -> None:
        """
        Write a Paragraph into the text area.
        :param p: A Paragraph instance.
        :return: None
        """
        self.BeginParagraphStyle(Strings.style_paragraph)
        for element in p.get_elements():
            self._write_text(element)
        self.Newline()
        self.EndParagraphStyle()

    def _write_text(self, element) -> None:
        """
        Write a textual element into the text area under the currently applied style.
        :param element: The text element instance to write.
        :return: None
        """
        if isinstance(element, Text):
            if element.is_bold():
                self.BeginBold()
            self.BeginTextColour(element.get_color())
            self.WriteText(element.get_text())
            self.EndTextColour()
            if element.is_bold():
                self.EndBold()
        elif isinstance(element, Break):
            self.Newline()
        elif isinstance(element, Link):
            self._insert_link(element.get_text()[0], element.get_id(), element.get_status_color())

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

        self.BeginStyle(url_style)
        self.BeginURL(link_id)
        self.WriteText(text)
        self.EndURL()
        self.EndStyle()

    def url_in_text_click_handler(self, evt: wx.TextUrlEvent) -> None:
        """
        Handles click on url links inside text.
        :param evt: Not used
        :return: None
        """
        link = self._document.find_link(evt.GetString())
        url = evt.GetString()
        link_text = self.GetRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
        if not link:
            # Create a new link
            link = Link(link_text, url, link_text, self._document.get_other_articles(),
                        self._document.get_working_directory())
            link.seo_test_self()

        link.set_text(link_text)
        edit_dialog = EditLinkDialog(self, link)
        result = edit_dialog.ShowModal()
        self._handle_link_edit(result, link, evt)
        edit_dialog.Destroy()

    def _handle_link_edit(self, result: int, link: Link, evt: wx.TextUrlEvent = None) -> None:
        """
        Handle actions needed after a link has been edited in the link edit dialog.
        :param result: The wx result ID_OK, ID_CANCEL from the edit dialog
        :param link: The modified Link instance
        :param evt: If an event is passed in it is used to find where to replace the link, otherwise the link is
        inserted into the current position.
        :return: None
        """
        # TODO catch any red incorrect links when doing seo when switching to a different document/save and turn doc red
        # TODO Deleted links are not removed from the document to make undo work, reconcile links and images on save.
        if not self.BatchingUndo():
            self.BeginBatchUndo(Strings.undo_last_action)
        stored_link = self._document.find_link(link.get_id())
        if result == wx.ID_OK:
            # Only add link that is not already in the list
            if not stored_link:
                self._document.add_link(link)
            # Replace the text with link
            self.Remove(evt.GetURLStart(), evt.GetURLEnd() + 1)
            self._insert_link(link.get_text()[0], link.get_id(), link.get_status_color())
        elif result == wx.ID_DELETE or result == wx.ID_CANCEL:
            if stored_link and result == wx.ID_CANCEL:
                if self.BatchingUndo():
                    self.EndBatchUndo()
                return
            else:
                style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
                style_range = rt.RichTextRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
                # If it is a new link remove the link style from the text
                self.SetStyleEx(style_range, style, rt.RICHTEXT_SETSTYLE_REMOVE | rt.RICHTEXT_SETSTYLE_WITH_UNDO)
                # Without moving the caret you can still type in the now incorrect url style.
                self.MoveLeft(0)
                self.Invalidate()
                self.Refresh()

        if self.BatchingUndo():
            self.EndBatchUndo()

        # Send an event to the main gui to signal document color change
        color_evt = wx.CommandEvent(wx.wxEVT_COLOUR_CHANGED, self.GetId())
        color_evt.SetEventObject(self)
        wx.PostEvent(self.GetEventHandler(), color_evt)

    # TODO insert video
    # TODO insert aside image
    def on_insert_image(self, evt: wx.CommandEvent) -> None:
        """

        :param evt: Not used
        :return: None
        """
        # TODO memory leak in orphaned images and link, maybe reconcile on idle.
        self._main_frame.tool_bar.EnableTool(self.img_tool_id, False)
        # Open image selection dialog


        # self._write_field(from_button=True)

        # Return focus to the text area.
        wx.CallLater(100, self.SetFocus)

    def _change_bold(self, evt: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        if self.HasSelection():
            self.BeginBatchUndo(Strings.undo_bold)
            self.BeginBold()
            bold_range = self.GetSelectionRange()
            for char in range(bold_range[0], bold_range[1]):
                if char + 1 > bold_range[1] + 1:
                    break
                single_range = rt.RichTextRange(char, char + 1)
                # Get the attributes of the single char range and modify them in place. Otherwise changing paragraph.
                # style is broken since the attributes are reset for the range.
                attr = rt.RichTextAttr()
                self.GetStyleForRange(single_range, attr)
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
                self.SetStyleEx(single_range, attr, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO)
            self.EndBatchUndo()
        else:
            if not self.IsSelectionBold():
                self.BeginBold()
            else:
                self.EndBold()
