from contextlib import contextmanager
from typing import List, Tuple

import wx
import wx.richtext as rt

from Constants.Constants import Strings, Numbers, Events
from Gui.Dialogs.EditLinkDialog import EditLinkDialog
from Gui.Dialogs.EditTextImageDialog import EditTextImageDialog
from Gui.Dialogs.EditVideoDialog import EditVideoDialog
from Tools.ConfigManager import ConfigManager
from Tools.Document.ArticleElements.Heading import Heading
from Tools.Document.ArticleElements.ImageInText import ImageInText
from Tools.Document.ArticleElements.Link import Link
from Tools.Document.ArticleElements.Paragraph import Paragraph
from Tools.Document.ArticleElements.Text import Text, Break
from Tools.Document.ArticleElements.UnorderedList import UnorderedList
from Tools.Document.ArticleElements.Video import Video
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.ImageTextField import ImageTextField
from Tools.SpellCheckerWithIgnoredList import SpellCheckerWithIgnoreList


class CustomRichText(rt.RichTextCtrl):
    """
    Custom rich text control
    """

    def __init__(self, img_tool_id: int, video_tool_id: int, style_control: wx.ListBox, parent, style):
        """
        Constructor for the custom rich text control.
        :param img_tool_id: ID of the insert image tool.
        :param video_tool_id: ID of the insert video tool.
        :param style_control: Style control from gui.
        :param parent: Parent of this control.
        :param style: wx style attributes.
        """
        super().__init__(parent, -1, style=style)
        # Required for copy/paste to work and retain text attributes.
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())
        self._parent = parent
        self._doc = None
        self._css_document = None
        self._img_tool_id = img_tool_id
        self._video_tool_id = video_tool_id
        # Used to prevent over-calling methods on keypress.
        self._disable_input = False
        self._click_counter = 0
        # Is set to True when a document is fully loaded, prevents setting document to modified before it is loaded.
        self._load_indicator = False
        # Used to distinguish paste
        self._paste_indicator = False
        self._config_manager = ConfigManager.get_instance()
        # This is used to control undo and redo
        self._command_processor: wx.CommandProcessor = self.GetCommandProcessor()
        # Fix behavior on X11 server
        wx.TheClipboard.UsePrimarySelection(False)

        self.AlwaysShowScrollbars(False, True)
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')

        self._style_picker = style_control

        # Used to store copied text elements in case they need to be pasted in different documents or after save
        self._link_lookaside = []
        self._image_lookaside = set()
        self._video_lookaside = set()
        # Registered fields are used to easily update colors of images and videos on spellcheck dictionary change
        self._fields = []

        # Used for three click whole paragraph select.
        self._three_click_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_click_timer, self._three_click_timer)

        # This is called too early before the config manager has loaded the full config and returns default language.
        # But language is updated when spellcheck runs since we can change language dynamically.
        self._checker = SpellCheckerWithIgnoreList(self._config_manager.get_spelling_lang())
        # Used for active spellcheck after modification.
        self._spelling_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_spelling_timer, self._spelling_timer)

        # Used to delay self test while fast edits are being made (holding a key).
        self._test_delay_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_test_delay_timer, self._test_delay_timer)

        self._main_frame = wx.GetTopLevelParent(self)
        self.Bind(wx.EVT_LISTBOX, self._style_picker_handler, self._style_picker)
        self.Bind(wx.EVT_TEXT_URL, self._url_in_text_click_handler, self)
        self.Bind(wx.EVT_TEXT, self._modification_handler, self)
        self.Bind(wx.EVT_MENU, self._on_insert_tool, self._main_frame.insert_img_tool)
        self.Bind(wx.EVT_MENU, self._on_insert_tool, self._main_frame.insert_video_tool)
        self.Bind(wx.EVT_MENU, self._change_bold, self._main_frame.bold_tool)

        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left)
        self.Bind(wx.EVT_MOTION, self._update_gui_handler)
        self.Bind(wx.EVT_LEFT_UP, self._update_gui_handler)

        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_KEY_UP, self._update_gui_handler)
        # Text paste handling.
        self.Bind(wx.EVT_MENU, self._paste_handler, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self._copy_handler, id=wx.ID_COPY)
        self.Bind(rt.EVT_RICHTEXT_CONTENT_INSERTED, self._paste_finish, self)

        # Disable drag and drop text.
        self.SetDropTarget(None)
        self._default_style: rt.RichTextAttr = self.GetDefaultStyleEx()

        self._add_text_handlers()
        self._create_styles()
        self._fill_style_picker()

    @contextmanager
    def load_indicator_manager(self) -> None:
        """
        Automatically manages load indicator that controls whether the document is fully loaded and modifications should
        make the document modified in the main gui.
        :return: None
        """
        # This happens before executing the managed code inside with.
        self._load_indicator = False
        # Here the code inside with is executed.
        yield
        # This happens after executing the managed code inside with.
        self._load_indicator = True

    # noinspection PyUnusedLocal
    def _modification_handler(self, event: wx.CommandEvent) -> None:
        """
        Set document to modified state when anything is written by sending the event to the main frame
        _text_area_edit_handler.
        :param event: Not used
        :return: None
        """
        if self._load_indicator:
            # Single shot set to True because the timer should not fire events unless started by this method.
            self._test_delay_timer.Start(Numbers.test_timeout, True)

    # noinspection PyUnusedLocal
    def _on_test_delay_timer(self, event: wx.CommandEvent) -> None:
        """
        When the timer runs out and if three left click were made, select whole current paragraph.
        :param event: Not used.
        :return: None
        """
        if self._load_indicator:
            self._send_color_event(True)
            if not self._spelling_timer.IsRunning():
                self._spelling_timer.Start(Numbers.spellcheck_timeout)

    def _send_color_event(self, modified: bool) -> None:
        """
        Send text changed event to the main gui to cause recoloring of the document and tell it whether the document
        should be set modified. We may not want to make the document modified when we just learned more words in
        spellcheck but did not change anything. This still needs to recolor the document though.
        :param modified: True if the document should be set modified.
        :return: None
        """
        color_evt = Events.TextChangedEvent(self.GetId())
        # Indicate that document should be set modified.
        if modified:
            color_evt.SetInt(1)
        else:
            color_evt.SetInt(0)
        wx.PostEvent(self.GetEventHandler(), color_evt)

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
        # Do not set specific font color, color is retained in each text object.
        stl_paragraph: rt.RichTextAttr = rt.RichTextAttr()
        stl_paragraph.SetFontSize(Numbers.paragraph_font_size)
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(0)
        stl_paragraph.SetParagraphSpacingAfter(0)
        stl_paragraph.SetParagraphStyleName(Strings.style_paragraph)
        # Used to identify text object children of paragraphs
        stl_paragraph.SetFontFaceName(Strings.style_paragraph)
        # Debug
        # stl_paragraph.SetBackgroundColour(wx.YELLOW)
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
        # Debug
        # stl_heading_3.SetBackgroundColour(wx.RED)
        style_h3: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_3)
        style_h3.SetStyle(stl_heading_3)
        style_h3.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h3)

        # Heading 4 style
        stl_heading_4: rt.RichTextAttr = rt.RichTextAttr()
        stl_heading_4.SetFontSize(Numbers.heading_4_size)
        stl_heading_4.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_4.SetFontWeight(wx.FONTWEIGHT_BOLD)
        stl_heading_4.SetParagraphSpacingBefore(int(Numbers.paragraph_spacing / 2))
        stl_heading_4.SetParagraphSpacingAfter(int(Numbers.paragraph_spacing / 2))
        stl_heading_4.SetParagraphStyleName(Strings.style_heading_4)
        stl_heading_4.SetFontFaceName(Strings.style_heading_4)
        # Debug
        # stl_heading_4.SetBackgroundColour(wx.BLUE)
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
        # Debug
        # stl_list.SetBackgroundColour(wx.GREEN)
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
        stl_link.SetURL(Strings.url_stub)
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

    def _change_style(self, buffer: rt.RichTextBuffer, style_name: str, position: int, preserve_url=True) -> None:
        """
        Changes the style of a paragraph or selection in the rich text control buffer visible on screen.
        :param buffer: The rich text buffer to work with.
        :param style_name: The name of a style in stylesheet.
        :param position: The position of the caret. This is needed because when changing style over multiple paragraphs
        the position is passed from selection. This is used when joining heading and ordinary paragraph using
        delete or backspace. If position is -1, the current caret position is used.
        :param preserve_url: True to preserve url when changing to paragraph style.
        :return: None
        """
        if position == -1:
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())

        self._change_style_in_buffer(buffer, style_name, position, preserve_url)

        if style_name == Strings.style_url:
            self._apply_url_style()

        # Unless we simulate a move, you can still type in the wrong style after change.
        self.Invalidate()
        self.Refresh()
        self.MoveRight(0)

    def _change_style_in_buffer(self, buffer: rt.RichTextBuffer, style: str, position: int, preserve_url=True) -> None:
        """
        Changes the style of a paragraph in the buffer.
        :param buffer: The rich text buffer to work with.
        :param style: The name of a style in stylesheet.
        :param position: The position of the caret.
        :param preserve_url: True to preserve url when changing to paragraph style.
        :return: None
        """
        if style == Strings.style_heading_3 or style == Strings.style_heading_4:
            self._apply_heading_style(buffer, style, position)

        elif style == Strings.style_paragraph:
            self._apply_paragraph_style(buffer, position, preserve_url)

        elif style == Strings.style_list:
            self._apply_list_style(buffer, position)

    @staticmethod
    def _apply_heading_style(buffer: rt.RichTextBuffer, heading_type: str, position: int) -> None:
        """
        Changes current paragraph under the cursor into a heading 3 or 4, removing any links.
        :param buffer: The rich text buffer to work with.
        :param heading_type: The heading style size.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = buffer.GetParagraphAtPosition(position)
        style: rt.RichTextAttr = buffer.GetStyleSheet().FindStyle(heading_type).GetStyle()
        p_range = p.GetRange().ToInternal()
        # Save the color of the first child, this color will be used for the whole text.
        color = p.GetChild(0).GetAttributes().GetTextColour()

        # Brute force the paragraph into the heading style paragraph attributes are reset completely which removes list
        # style. Character attributes are changed but not reset. Specific attributes are then changed separately.
        end_batch = False
        if not buffer.SuppressingUndo() and not buffer.BatchingUndo():
            # Only batch undo if we are not already recording changes from the beginning of modify text method.
            # Basically only if this method is called from the style picker.
            buffer.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        buffer.SetStyle(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY |
                        rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            buffer.EndBatchUndo()

        # The paragraph changes after style set, so find it again.
        p = buffer.GetParagraphAtPosition(position)
        # Restore and set only relevant attributes for the style.
        for child in p.GetChildren():
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontSize(style.GetFontSize())
            attrs.SetFontWeight(wx.FONTWEIGHT_BOLD)
            attrs.SetBackgroundColour(style.GetBackgroundColour())
            attrs.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore())
            attrs.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter())
            attrs.SetFontFaceName(style.GetFontFaceName())
            attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            attrs.SetTextColour(color)
            # Only links can be underlined, it is safe to remove it here.
            attrs.SetFontUnderlined(style.GetFontUnderlined())
            if attrs.HasURL():
                # If any child has an url flag, remove it and set font color to normal.
                attrs.SetURL('')
                attrs.SetFlags(attrs.GetFlags() ^ wx.TEXT_ATTR_URL)
                attrs.SetTextColour(style.GetTextColour())
                attrs.SetCharacterStyleName('')

    @staticmethod
    def _apply_paragraph_style(buffer: rt.RichTextBuffer, position: int, preserve_url: bool) -> None:
        """
        Changes current paragraph under the cursor into the paragraph style defined for normal text.
        Keeps link attr, text weight and color.
        :param buffer: The rich text buffer to work with.
        :param position: The position of the caret.
        :param preserve_url: True to preserve urls.
        :return: None
        """
        p: rt.RichTextParagraph = buffer.GetParagraphAtPosition(position)
        # This is needed to prevent loss of children attributes when typing quickly for some reason.
        p.Defragment(rt.RichTextDrawingContext(p.GetBuffer()))
        style: rt.RichTextAttr = buffer.GetStyleSheet().FindStyle(Strings.style_paragraph).GetStyle()
        # The GetRange.To/FromInternal is causing problems with turning list to paragraph here.
        p_range: rt.RichTextRange = p.GetRange()
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
        if not buffer.SuppressingUndo() and not buffer.BatchingUndo():
            buffer.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        buffer.SetStyle(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY |
                        rt.RICHTEXT_SETSTYLE_RESET)
        if end_batch:
            buffer.EndBatchUndo()

        p = buffer.GetParagraphAtPosition(position)
        for child, attr_dict in zip(p.GetChildren(), child_list):
            attrs: rt.RichTextAttr = child.GetAttributes()
            attrs.SetFontWeight(attr_dict['weight'])
            attrs.SetBackgroundColour(style.GetBackgroundColour())
            attrs.SetFontSize(style.GetFontSize())
            attrs.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore())
            attrs.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter())
            attrs.SetFontFaceName(Strings.style_paragraph)
            attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
            if attrs.HasURL() and preserve_url:
                # Only urls have background color and underline.
                attrs.SetBackgroundColour(attr_dict['background'])
                attrs.SetFontUnderlined(True)
                attrs.SetFontFaceName(Strings.style_url)
            else:
                # Remove the url
                attrs.SetURL('')
                attrs.SetFlags(attrs.GetFlags() ^ wx.TEXT_ATTR_URL)
                attrs.SetCharacterStyleName('')
                attrs.SetFontUnderlined(False)

    @staticmethod
    def _apply_list_style(buffer: rt.RichTextBuffer, position: int) -> None:
        """
        Changes paragraph on position into list item.
        :param buffer: The rich text buffer to work with.
        :param position: The position of the caret.
        :return: None
        """
        p: rt.RichTextParagraph = buffer.GetParagraphAtPosition(position)
        p.Defragment(rt.RichTextDrawingContext(p.GetBuffer()))
        style_def: rt.RichTextListStyleDefinition = buffer.GetStyleSheet().FindStyle(Strings.style_list)
        style: rt.RichTextAttr = style_def.GetStyle()
        p_range = p.GetRange().ToInternal()
        child_list = []
        for child in p.GetChildren():
            child: rt.RichTextPlainText
            saved_attrs = {}
            # The built-in wx Copy method causes the children to disappear for a wtf reason.
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
        if not buffer.SuppressingUndo() and not buffer.BatchingUndo():
            buffer.BeginBatchUndo(Strings.undo_last_action)
            end_batch = True
        buffer.SetStyle(p_range, style, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_PARAGRAPHS_ONLY |
                        rt.RICHTEXT_SETSTYLE_RESET)
        buffer.SetListStyle(p_range, style_def, specifiedLevel=0, flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO |
                            rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL)
        if end_batch:
            buffer.EndBatchUndo()

        p = buffer.GetParagraphAtPosition(position)
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
            link_range: rt.RichTextRange = self.GetSelectionRange()
            self.SetStyleEx(link_range, self._stylesheet.FindStyle(Strings.style_url).GetStyle(),
                            flags=rt.RICHTEXT_SETSTYLE_WITH_UNDO | rt.RICHTEXT_SETSTYLE_CHARACTERS_ONLY)
            if self.DoesSelectionHaveTextEffectFlag(wx.TEXT_ATTR_EFFECT_STRIKETHROUGH):
                self.BeginSuppressUndo()
                self.apply_effect(False, link_range)
                self.EndSuppressUndo()

    @staticmethod
    def get_style_at_pos(buffer: rt.RichTextBuffer, position) -> (str, str):
        """
        Get the style name at given position in the text.
        :param position: The position.
        :param buffer: The buffer to work with.
        :return: (paragraph style name, character style name) or (None, None).
        """
        style_carrier = rt.RichTextAttr()
        paragraph_style_name = None
        character_style_name = None
        buffer.GetStyle(position, style_carrier)
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
        paragraph_style_name, character_style_name = self.get_style_at_pos(self.GetBuffer(),
                                                                           self.GetAdjustedCaretPosition
                                                                           (self.GetCaretPosition()))
        if character_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(character_style_name))
        elif paragraph_style_name:
            self._style_picker.SetSelection(self._style_picker.FindString(paragraph_style_name))

    def _modify_text(self) -> None:
        """
        Handle keypress events. Runs on key down.
        :return: None
        """
        # Disable other keyboard input while this method is working.
        self._disable_input = True

        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        paragraph_style, character_style = self.get_style_at_pos(self.GetBuffer(), position)

        # End url style if next character has different or no url.
        if character_style == Strings.style_url:
            style_carrier = rt.RichTextAttr()
            self.GetStyle(position, style_carrier)
            current_url = style_carrier.GetURL()
            self.GetStyle(position + 1, style_carrier)
            next_url = style_carrier.GetURL()
            if not next_url or current_url != next_url or position == (p.GetRange()[1] - 1):
                # End url style if we are at th end of an url, between different urls or at the end of paragraph.
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
                self._change_style(self.GetBuffer(), Strings.style_paragraph, position=-1)
                paragraph_style = Strings.style_paragraph
                p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)

        # Turn empty lines into paragraph style. Also turns deleted images into paragraph style.
        elif not p.GetTextForRange(p.GetRange()):
            attrs: rt.RichTextAttr = p.GetAttributes()
            if attrs.GetBulletStyle() != wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                if not isinstance(p.GetChild(0), rt.RichTextField):
                    # Field is not seen as text.
                    self._change_style(self.GetBuffer(), Strings.style_paragraph, position=-1, preserve_url=False)
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
                self._change_style(self.GetBuffer(), font_face, position=-1)
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
            # and not first style was in the condition below
            if attrs.GetBulletStyle() == wx.TEXT_ATTR_BULLET_STYLE_STANDARD:
                # Empty list line has no child and no first style.
                first_style = Strings.style_list
            if first_style == Strings.style_url:
                first_style = paragraph_style

            # Test all children, maybe we do not need to change the style.
            style_set = set()
            font_face = None
            for child in p.GetChildren():
                attrs: rt.RichTextAttr = child.GetAttributes()
                font_face = attrs.GetFontFaceName()
                style_set.add(font_face)
            if len(style_set) != 1 and style_set != {Strings.style_paragraph, Strings.style_url} and style_set != \
                    {Strings.style_list, Strings.style_url}:
                # Skip changing style if there is only one style in the set or the set only contains paragraph/list
                # style and url style, otherwise change the style.
                self._change_style(self.GetBuffer(), first_style, position=-1)
            elif font_face != paragraph_style:
                # Used for fixing pasted styles which are wrong for some reason.
                self._change_style(self.GetBuffer(), first_style, position=-1)

        self._update_style_picker()
        self.enable_buttons()

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

        # Do not run this method when we press ctrl. Events for ctrl-z are EVT_MENU. Also skip special keys.
        if event.ControlDown() or event.ShiftDown() or event.AltDown() or event.GetKeyCode() == wx.WXK_CAPITAL:
            # Skip is needed for keyboard menu shortcuts to work.
            event.Skip()
            return

        if not self.BatchingUndo():
            # Start batch here because delete text would go through before the batch would be started in modify text.
            self.BeginBatchUndo(Strings.undo_last_action)

        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        paragraph_style, character_style = self.get_style_at_pos(self.GetBuffer(), position)
        # Detect paragraph beginning. Allow pressing return at the beginning of line.
        paragraph_start = self.GetFocusObject().GetParagraphAtPosition(position).GetRange()[0]
        if paragraph_start != position:
            _, next_character_style = self.get_style_at_pos(self.GetBuffer(), position + 1)
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
        # Calls the function when the current event handler has exited. wx.EVT_TEXT can not be used because it does not
        # fire on list bullet deletion.
        wx.CallAfter(self._modify_text)

    def _copy_handler(self, event: wx.CommandEvent) -> None:
        """
        Runs a method scheduled right after this handler finishes. Runs on evt_menu - ID_COPY.
        :param event: Not used.
        :return: None
        """
        event.Skip()
        wx.CallAfter(self._backup_copied_elements)

    def _backup_copied_elements(self) -> None:
        """
        Backs up links, urls and video elements from the text which is being copied. This allows to paste text correctly
        even after the document has been saved after the original text was removed.
        :return: None
        """
        # Clear current lookaside lists.
        self._link_lookaside.clear()
        self._video_lookaside.clear()
        self._image_lookaside.clear()

        text_data = rt.RichTextBufferDataObject()
        success = None
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        if success:
            copy_buffer: rt.RichTextBuffer = text_data.GetRichTextBuffer()
            # Search for urls, images and videos in the pasted text and back them up.
            paragraphs: List[rt.RichTextParagraph] = copy_buffer.GetChildren()
            for p in paragraphs:
                par_style: str = p.GetAttributes().GetFontFaceName()
                if par_style == Strings.style_paragraph:
                    for child in p.GetChildren():
                        child: rt.RichTextPlainText
                        attrs: rt.RichTextAttr = child.GetAttributes()
                        if attrs.HasURL():
                            # Find the copied link in the lookaside.
                            self._link_lookaside.append(self._doc.find_link(attrs.GetURL()))

                for child in p.GetChildren():
                    # Find images and videos.
                    if isinstance(child, rt.RichTextField):
                        field_type: str = child.GetProperties().GetProperty(Strings.field_type)
                        if field_type == Strings.field_image:
                            self._image_lookaside.add(self._doc.find_in_text_image(child.GetFieldType()))
                        else:
                            self._video_lookaside.add(self._doc.find_video(child.GetFieldType()))

    def _paste_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle text paste into the control. Runs before the text is pasted. Runs on evt_menu - ID_PASTE
        Pasting a field does not work correctly when using x11 on linux.
        :param event: Passed to other methods.
        :return: None
        """
        if self._prevent_paste(event):
            return

        # Indicate paste to the paste finish handler.
        self._paste_indicator = True
        text_data = rt.RichTextBufferDataObject()
        success = False
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        if success:
            paste_position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
            paste_buffer: rt.RichTextBuffer = text_data.GetRichTextBuffer()
            # We need the stylesheet to change styles in the buffer before pasting.
            paste_buffer.SetStyleSheet(self._stylesheet)
            paste_buffer.BeginSuppressUndo()
            ctrl_buffer: rt.RichTextBuffer = self.GetBuffer()
            current_style = self.get_style_at_pos(ctrl_buffer, paste_position)

            # Turn the style of the first paragraph into the correct style.
            first_buffer_style = self.get_style_at_pos(paste_buffer, 0)
            if current_style[1] == Strings.style_url:
                paragraphs: List[rt.RichTextParagraph] = paste_buffer.GetChildren()
                if len(paragraphs) > 1:
                    # Prevent pasting multiple paragraphs into an url.
                    wx.MessageBox(Strings.warning_paste_into_url, Strings.status_error, wx.OK | wx.ICON_ERROR)
                    return
                elif paste_buffer.GetChildCount() == 1 and isinstance(paste_buffer.GetChild(0).GetChild(0),
                                                                      rt.RichTextField):
                    # Do not allow pasting images into urls.
                    return
                else:
                    # Paste as plain text.
                    text = paragraphs[0].GetTextForRange(paragraphs[0].GetRange())
                    ctrl_buffer.InsertTextWithUndo(self.GetCaretPosition() + 1, text, self, 0)
                    return
            elif first_buffer_style[0] == Strings.style_image:
                # if the first style is image, paste on new line if we are not on an empty line to preserve style.
                p = ctrl_buffer.GetParagraphAtPosition(self.GetAdjustedCaretPosition(self.GetCaretPosition()))
                if p.GetChild(0).GetText():
                    # This messes up the caret position because of the self, so we must restore it.
                    # Set the style to the current style before adding the new line, otherwise the current line changes.
                    paste_buffer.SetDefaultStyle(paste_buffer.GetStyleSheet().FindStyle(current_style[0]).GetStyle())
                    if current_style[0] == Strings.style_list:
                        paste_buffer.InsertTextWithUndo(0, '\n', self)
                        style_def = paste_buffer.GetStyleSheet().FindStyle(Strings.style_list)
                        paste_buffer.SetListStyle((0, 0), style_def, specifiedLevel=0,
                                                  flags=rt.RICHTEXT_SETSTYLE_SPECIFY_LEVEL)
                    else:
                        paste_buffer.InsertTextWithUndo(0, '\n', self)
                    self.SetCaretPosition(paste_position)
            elif first_buffer_style != current_style:
                # Only change the style when we are pasting into a different style.
                self._change_style_in_buffer(paste_buffer, current_style[0], 0)
            # Search for urls, images and videos in the pasted text and make a copy in the lists.
            paragraphs: List[rt.RichTextParagraph] = paste_buffer.GetChildren()
            for p in paragraphs:
                par_style: str = p.GetAttributes().GetFontFaceName()
                if par_style == Strings.style_paragraph:
                    for child in p.GetChildren():
                        child: rt.RichTextPlainText
                        attrs: rt.RichTextAttr = child.GetAttributes()
                        if attrs.HasURL():
                            # Find the copied link in the lookaside.
                            stored_link = None
                            for link in self._link_lookaside:
                                if link:
                                    if link.get_id() == attrs.GetURL():
                                        stored_link = link
                                    # Create a copy of the found link to allow independent modification.
                                    # TODO broken when the pasted selection has an OK link and a red link
                                    new_link = Link(stored_link.get_text()[0], stored_link.get_url()[0],
                                                    stored_link.get_title()[0], self._doc.get_other_articles(),
                                                    self._doc.get_working_directory())
                                    new_link.test_self(self._config_manager.get_online_test())
                                    self._doc.add_link(new_link)
                                    # Set the new id to the pasted url to differentiate them.
                                    attrs.SetURL(new_link.get_id())
                                else:
                                    # None link is a new red empty one.
                                    # Create a new empty separate link.
                                    new_link = Link(child.GetText(), Strings.url_stub, child.GetText(),
                                                    self._doc.get_other_articles(),
                                                    self._doc.get_working_directory())
                                    new_link.test_self(self._config_manager.get_online_test())

                                    self._doc.add_link(new_link)
                                    # Set the new id to the pasted url to differentiate them.
                                    attrs.SetURL(new_link.get_id())
                stored_element = None
                new_field = None
                for child in p.GetChildren():
                    # Find images and videos.
                    if isinstance(child, rt.RichTextField):
                        field_type: str = child.GetProperties().GetProperty(Strings.field_type)
                        if field_type == Strings.field_image:
                            for img in self._image_lookaside:
                                if img.get_id() == child.GetFieldType():
                                    stored_element = img
                        else:
                            for video in self._video_lookaside:
                                if video.get_id() == child.GetFieldType():
                                    stored_element = video
                    if stored_element:
                        # Create a copy of the video/image.
                        if isinstance(stored_element, ImageInText):
                            new_field = ImageInText(stored_element.get_link_title()[0],
                                                    stored_element.get_image_alt()[0],
                                                    stored_element.get_original_image_path(),
                                                    stored_element.get_thumbnail_image_path(),
                                                    stored_element.get_full_filename(),
                                                    stored_element.get_thumbnail_filename())
                            new_field.test_self()
                            self._doc.add_image(new_field)
                        elif isinstance(stored_element, Video):
                            new_field = Video(stored_element.get_title()[0],
                                              stored_element.get_size()[0],
                                              stored_element.get_size()[1],
                                              stored_element.get_url()[0])
                            new_field.test_self(self._config_manager.get_online_test())
                            self._doc.add_video(new_field)
                        self._register_field(new_field)
                        child.SetFieldType(new_field.get_id())
            if len(paste_buffer.GetChildren()) > 1:
                # Add empty paragraph after the pasted text. This paragraph retains the original style from the point of
                # paste. The paragraph will be removed later if empty. Catches image fields because a field has an
                # empty line added to the front.
                paste_buffer.AddParagraph('')
            elif paste_buffer.GetChildCount() == 1 and isinstance(paste_buffer.GetChild(0).GetChild(0),
                                                                  rt.RichTextField):
                # add empty line to image which is pasted alone on an empty line.
                paste_buffer.AddParagraph('')

            # Only add 1 to paste position when we are not on an empty line.
            p: rt.RichTextParagraph = ctrl_buffer.GetParagraphAtPosition(paste_position)
            if p.GetChildCount() >= 1:
                if p.GetChild(0).GetText():
                    # We are not on an empty line.
                    if p.GetRange().GetStart() == paste_position:
                        if paste_buffer.GetChildCount() > 1 and paste_buffer.GetChildren()[1].GetChildCount() > 0:
                            if isinstance(paste_buffer.GetChildren()[1].GetChildren()[0], rt.RichTextField):
                                # We are pasting an image. The first child will be an empty line.
                                # Works with text not with images, paste around the 1st character is always wrong.
                                ctrl_buffer.InsertParagraphsWithUndo(self.GetCaretPosition(), paste_buffer, self, 0)
                                paste_buffer.EndSuppressUndo()
                                return
                        else:
                            # For some reason we can not use the adjusted position here.
                            # Pasting just text not beginning with an image onto a non-empty line.
                            ctrl_buffer.InsertParagraphsWithUndo(self.GetCaretPosition() + 1, paste_buffer, self, 0)
                            paste_buffer.EndSuppressUndo()
                            return
            # Pasting onto an empty line
            ctrl_buffer.InsertParagraphsWithUndo(self.GetCaretPosition() + 1, paste_buffer, self, 0)
            paste_buffer.EndSuppressUndo()
        else:
            # Skip when just plain text from outside the editor and let the control paste in current style.
            event.Skip()

    def _prevent_paste(self, event: wx.CommandEvent) -> bool:
        """
        Prevent paste if we are in an image style.
        :param event: Used to get id.
        :return: True when paste should not be allowed.
        """
        if event.GetId() == wx.ID_PASTE:
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
            paragraph_style, _ = self.get_style_at_pos(self.GetBuffer(), position)
            # We get here without starting undo batch, since on key down ignores ctrl.
            # Start paste batch here because delete text would go through before the batch would be started
            # in modify text.
            self.BeginBatchUndo(Strings.undo_last_action)
            if paragraph_style == Strings.style_image:
                return True
        return False

    # noinspection PyUnusedLocal
    def _paste_finish(self, event: rt.RichTextEvent) -> None:
        """
        Finish pasting a new text. Delete the additional empty paragraph to work around the weird behavior of last
        paragraph being pasted in the style of the paste start point.
        :param event: Not used.
        :return: None
        """
        if self._paste_indicator:
            self._paste_indicator = False
            if self.BatchingUndo():
                # Causes segfault if called directly.
                wx.CallAfter(self.EndBatchUndo)

    def _update_gui_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle key events to update GUI controls.
        :param event: Not used.
        :return: None
        """
        if self.HasFocus():
            self.enable_buttons()
        event.Skip()

    def _on_mouse_left(self, event: wx.MouseEvent) -> None:
        """
        Handle left mouse click. Starts a timer and counts left mouse clicks in order to allow three click select.
        :param event: Not used.
        :return: None
        """
        self._update_style_picker()
        if not self._three_click_timer.IsRunning():
            self._three_click_timer.Start(Numbers.three_click_timeout)
        self._click_counter = self._click_counter + 1
        event.Skip()

    # noinspection PyUnusedLocal
    def _on_click_timer(self, event: wx.CommandEvent) -> None:
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
        self._three_click_timer.Stop()

    # noinspection PyUnusedLocal
    def _on_spelling_timer(self, event: wx.CommandEvent) -> None:
        """
        When the timer runs out and if three left click were made, select whole current paragraph.
        :param event: Not used.
        :return: None
        """
        self.run_spellcheck()

    def run_spellcheck(self) -> None:
        """
        Run spellcheck on text to underline bad words.
        :return: None
        """
        self._spelling_timer.Stop()
        self.BeginSuppressUndo()
        # The word selection would move the caret if the position was not restored.
        position = self.GetCaretPosition()
        # Apply twice to remove and reapply
        self.SelectAll()
        self.apply_effect(False, self.GetSelectionRange())
        self.SelectNone()
        self._checker.reload_language()
        self._checker.set_text(self.get_text())
        for _ in self._checker:
            word_range = rt.RichTextRange(self._checker.wordpos, (self._checker.wordpos + len(self._checker.word)))
            attrs = rt.RichTextAttr()
            attrs.SetFontFaceName(Strings.style_url)
            if not self.HasCharacterAttributes(word_range, attrs):
                self.apply_effect(True, word_range)
            self.SelectNone()

        self.SetCaretPosition(position)
        self.EndSuppressUndo()

    def apply_effect(self, enable: bool, text_range: rt.RichTextRange) -> None:
        """
        Apply text effect to range of characters.
        :param enable: True to turn effect on.
        :param text_range: Range for the effect.
        :return: None
        """
        effect = wx.TEXT_ATTR_EFFECT_STRIKETHROUGH
        attrs: rt.RichTextAttr = rt.RichTextAttr()
        attrs.SetFlags(wx.TEXT_ATTR_EFFECTS)
        attrs.SetTextEffectFlags(effect)
        if enable:
            attrs.SetTextEffects(effect)
        else:
            attrs.SetTextEffects(attrs.GetTextEffectFlags() & ~effect)
        self.SetStyleEx(text_range, attrs)

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
                        self._change_style(self.GetBuffer(), evt.GetString(), position)
        else:
            self._change_style(self.GetBuffer(), evt.GetString(), position=-1)

        self._send_color_event(True)
        self.EndBatchUndo()
        # Return focus back into the text area. The focus must happen a little later when the style picker is finished.
        wx.CallLater(100, self.SetFocus)

    def enable_buttons(self) -> None:
        """
        Enable or disable styling buttons based on caret position.
        :return: None
        """
        position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
        paragraph_style, character_style = self.get_style_at_pos(self.GetBuffer(), position)
        p: rt.RichTextParagraph = self.GetFocusObject().GetParagraphAtPosition(position)
        if not p.GetTextForRange(p.GetRange()) and paragraph_style == Strings.style_paragraph \
                and not isinstance(p.GetChild(0), rt.RichTextField):
            # Only allow inserting images on an empty paragraph line with no other images.
            self._main_frame.tool_bar.EnableTool(self._img_tool_id, True)
            self._main_frame.tool_bar.EnableTool(self._video_tool_id, True)
        else:
            self._main_frame.tool_bar.EnableTool(self._img_tool_id, False)
            self._main_frame.tool_bar.EnableTool(self._video_tool_id, False)
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
        self._load_indicator = False
        self._fields.clear()
        # Set default attributes. Copied from wxPython source code.
        self.SetFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
        attrs: rt.RichTextAttr = rt.RichTextAttr()
        attrs.SetFont(self.GetFont())
        attrs.SetTextColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        attrs.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        attrs.SetLineSpacing(10)
        attrs.SetParagraphSpacingAfter(10)
        attrs.SetParagraphSpacingBefore(0)
        self.SetBasicStyle(attrs)

        self.SetMargins(5, 5)

        # The default attributes will be merged with base attributes, so can be empty to begin with.
        self.SetDefaultStyle(rt.RichTextAttr())

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.GetBuffer().Reset()
        self.GetBuffer().SetRichTextCtrl(self)
        self.GetBuffer().CleanUpFieldTypes()
        self.GetBuffer().ResetAndClearCommands()
        self.GetBuffer().Invalidate(rt.RICHTEXT_ALL)

        self.Clear()
        self.SetModified(False)

    def set_content(self, doc: WhitebearDocumentArticle) -> None:
        """
        Set the document this text area is displaying.
        :param doc: The white bear article.
        :return: None
        """
        self._doc = doc
        self._css_document = doc.get_css_document()
        self.BeginSuppressUndo()
        self.clear_self()

        last_was_paragraph = False
        for element in doc.get_main_text_elements():
            if isinstance(element, Paragraph):
                if last_was_paragraph:
                    # Insert empty line.
                    self.BeginParagraphStyle(Strings.style_paragraph)
                    self.Newline()
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
        self.run_spellcheck()
        self._load_indicator = True
        # Set focus to the text area.
        wx.CallLater(100, self.SetFocus)

    def replace_string_with_style(self, replacement: str) -> None:
        """
        Replace selected string in the control with a different string and keep the style.
        :param replacement: New string
        :return: None
        """
        selection: rt.RichTextSelection = self.GetSelection()
        # Range is one char off for some reason.
        selection_range = rt.RichTextRange(selection.GetRange()[0], selection.GetRange()[1] + 1)
        self.Delete(selection_range)
        self.WriteText(replacement)

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
        field: rt.RichTextField = buffer.InsertFieldWithUndo(self.GetBuffer(), position, new_field.GetName(),
                                                             rt.RichTextProperties(), self, rt.RICHTEXT_INSERT_NONE,
                                                             rt.RichTextAttr())
        # Set property of the field to distinguish between image and video.
        if isinstance(element, Video):
            field_type = Strings.field_video
        else:
            field_type = Strings.field_image
        properties: rt.RichTextProperties = field.GetProperties()
        properties.SetProperty(Strings.field_type, field_type)
        self.EndBatchUndo()

    def _register_field(self, element) -> ImageTextField:
        """
        Register a new custom field that represent an image.
        :param element: The Video or ImageInText to display.
        :return: None
        """
        field_type = ImageTextField(element, self._doc.get_working_directory())
        self._fields.append(field_type)
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
            self.BeginTextColour(self._css_document.translate_str_color(element.get_color()))
            self.WriteText(element.get_text())
            self.EndTextColour()
            if element.is_bold():
                self.EndBold()
        elif isinstance(element, Break):
            self.Newline()
        elif isinstance(element, Link):
            self._insert_link(element.get_text()[0], element.get_id(), element.get_status_color())

    def _url_in_text_click_handler(self, evt: wx.TextUrlEvent) -> None:
        """
        Handles click on url links inside text.
        :param evt: Not used
        :return: None
        """
        link = self._doc.find_link(evt.GetString())
        url = evt.GetString()
        link_text = self.GetRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
        if not link:
            # Create a new link
            link = Link(link_text, url, link_text, self._doc.get_other_articles(),
                        self._doc.get_working_directory())
            link.test_self(self._config_manager.get_online_test())

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
        # Deleted links are not removed from the document to make undo work.
        stored_link = self._doc.find_link(link.get_id())
        if stored_link and result == wx.ID_CANCEL:
            # No change needed.
            return

        if link.is_modified() or result == wx.ID_DELETE:
            if not self.BatchingUndo():
                self.BeginBatchUndo(Strings.undo_last_action)
            if result == wx.ID_OK:
                # Only add link that is not already in the list
                if not stored_link:
                    self._doc.add_link(link)
                # Replace the text with link
                self.Remove(evt.GetURLStart(), evt.GetURLEnd() + 1)
                self._insert_link(link.get_text()[0], link.get_id(), link.get_status_color())
            elif result == wx.ID_DELETE:
                # The DELETE button was pressed:
                style: rt.RichTextAttr = self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle()
                style_range = rt.RichTextRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
                # If it is a new link remove the link style from the text
                self.SetStyleEx(style_range, style, rt.RICHTEXT_SETSTYLE_REMOVE | rt.RICHTEXT_SETSTYLE_WITH_UNDO)
                # Without moving the caret you can still type in the now incorrect url style.
                self.MoveLeft(0)
                self.Invalidate()
                self.Refresh()
                self._send_color_event(True)
        else:
            self._send_color_event(link.is_modified())

        if self.BatchingUndo():
            self.EndBatchUndo()

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
            # Links do not turn white with null color so use white.
            url_style.SetBackgroundColour(wx.WHITE)

        self.BeginStyle(url_style)
        self.BeginURL(link_id)
        self.WriteText(text)
        self.EndURL()
        self.EndStyle()

    def update_seo_colors(self) -> None:
        """
        Update the color of all links and images/videos in this document based on their seo status.
        :return: None.
        """
        # Changing paragraph style inside the loop changes address in memory and causes segfault. Create a list of
        # ranges to change and change the colors in a separate loop.
        ranges_list: List[Tuple[Tuple[int, int], Link]] = []
        buffer: rt.RichTextBuffer = self.GetBuffer()
        paragraphs: List[rt.RichTextParagraph] = buffer.GetChildren()
        for p in paragraphs:
            par_style: str = p.GetAttributes().GetFontFaceName()
            # Update links.
            if par_style == Strings.style_paragraph or par_style == Strings.style_list:
                for child in p.GetChildren():
                    child: rt.RichTextPlainText
                    attrs: rt.RichTextAttr = child.GetAttributes()
                    if attrs.HasURL():
                        stored_link: Link = self._doc.find_link(attrs.GetURL())
                        if stored_link:
                            stored_link.set_text(child.GetText())
                            stored_link.test_self(False)
                            ranges_list.append((child.GetRange(), stored_link))

        for link_range, link in ranges_list:
            # for some reason changing style on a link does not work, starting before the link does, but destroys the
            # style. So instead we replace the whole link.
            attr = rt.RichTextAttr()
            self.GetStyleForRange(link_range, attr)
            if attr.GetBackgroundColour() != link.get_status_color():
                self.BeginSuppressUndo()
                with self.load_indicator_manager():
                    self.Remove(link_range[0], link_range[1] + 1)
                    self._insert_link(link.get_text()[0], link.get_id(), link.get_status_color())
                # If the refresh is not there, font breaks if you use undo and the spellcheck again.
                self.MoveLeft(0)
                self.Invalidate()
                self.Refresh()
                self.EndSuppressUndo()

        # Update images and videos
        for field in self._fields:
            field.update_image()

    def _on_insert_tool(self, evt: wx.CommandEvent) -> None:
        """
        Insert a new image or video in the current location in the text field.
        :param evt: Used to get tool id.
        :return: None
        """
        self._main_frame.tool_bar.EnableTool(evt.GetId(), False)
        # Create a new placeholder text image or video
        if evt.GetId() == self._img_tool_id:
            new_element = ImageInText('', '', '', '', Strings.label_none, Strings.label_none)
            # This will set the image internal state to missing image placeholder.
            new_element.test_self()
        else:
            new_element = Video('', Numbers.video_width, Numbers.video_height, Strings.url_stub)
            new_element.test_self(self._config_manager.get_online_test())
        # Open edit dialog.
        if evt.GetId() == self._img_tool_id:
            edit_dialog = EditTextImageDialog(self._parent, new_element, self._doc.get_working_directory())
        else:
            edit_dialog = EditVideoDialog(self._parent, new_element)
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            # Send an event to the main gui to signal document color change
            if evt.GetId() == self._img_tool_id:
                self._doc.add_image(new_element)
            else:
                self._doc.add_video(new_element)
            self._write_field(new_element, from_button=True)

            self._send_color_event(True)
        edit_dialog.Destroy()
        # Return focus to the text area.
        wx.CallLater(100, self.SetFocus)

    # noinspection PyUnusedLocal
    def _change_bold(self, event: wx.CommandEvent) -> None:
        """
        Make text bold and vice versa.
        :param event: Not used
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
                # Get the attributes of the single char range and modify them in place. Otherwise, changing paragraph.
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
                self.SelectNone()
            self.EndBatchUndo()
            self._send_color_event(True)
        else:
            # Prevent beginning bold inside urls and headings.
            position = self.GetAdjustedCaretPosition(self.GetCaretPosition())
            par_style, char_style = self.get_style_at_pos(self.GetBuffer(), position)
            if char_style == Strings.style_url:
                return
            elif par_style == Strings.style_heading_3 or par_style == Strings.style_heading_4:
                return
            if not self.IsSelectionBold():
                self.BeginBold()
            else:
                self.EndBold()

    def get_text(self) -> str:
        """
        Returns the contents of the text field as a string with new lines in place of images and videos.
        This helps with searching in the field based on index because the GetValue method omits images and videos.
        :return: The contents of the text field as a string with new line characters in place of images and videos.
        """
        full_text: str = ''
        buffer: rt.RichTextBuffer = self.GetBuffer()
        paragraphs: List[rt.RichTextParagraph] = buffer.GetChildren()
        if paragraphs:
            if isinstance(paragraphs[0].GetChild(0), rt.RichTextField):
                # For some reason when the first paragraph is a field the special character is not necessary.
                full_text = '\n'
            else:
                full_text = paragraphs[0].GetTextForRange(paragraphs[0].GetRange())
        for p in list(paragraphs)[1:]:
            if isinstance(p.GetChild(0), rt.RichTextField):
                # Images and videos are Fields and these paragraph contain no characters and throw off index.
                # Use a special unsearchable character.
                full_text = full_text + Numbers.blank_character + '\n'
            else:
                full_text = full_text + '\n' + p.GetTextForRange(p.GetRange())
        return full_text

    def convert_document(self) -> None:
        """
        Create an internal representation of the document using the article elements classes.
        :return: None
        """
        # TODO titles are somehow cut short sometimes.
        self._doc: WhitebearDocumentArticle
        last_was_paragraph = False
        last_was_list = False
        new_text_elements = []
        buffer: rt.RichTextBuffer = self.GetBuffer()
        paragraphs: List[rt.RichTextParagraph] = buffer.GetChildren()
        for p in paragraphs:
            par_style: str = p.GetAttributes().GetFontFaceName()
            if par_style == Strings.style_paragraph:
                last_was_list = False
                next_p: Paragraph = self._convert_paragraph(p)
                if last_was_paragraph and new_text_elements[-1]:
                    # Reuse last Paragraph instance and join it together with a Break.
                    last_p: Paragraph = new_text_elements[-1]
                    if next_p:
                        last_p.add_element(Break())
                        last_p.extend_elements(next_p)
                        last_was_paragraph = True
                    else:
                        last_was_paragraph = False
                else:
                    if next_p:
                        # Do not append empty paragraphs.
                        new_text_elements.append(next_p)
                    # Skip multiple empty paragraphs which are translated to line breaks.
                    if p.GetTextForRange(p.GetRange()):
                        last_was_paragraph = True
            elif par_style == Strings.style_heading_3 or par_style == Strings.style_heading_4:
                last_was_paragraph = False
                last_was_list = False
                new_text_elements.append(self._convert_heading(p))
            elif par_style == Strings.style_list:
                last_was_paragraph = False
                new_p: Paragraph = self._convert_paragraph(p)
                if last_was_list:
                    current_list: UnorderedList = new_text_elements[-1]
                    if new_p:
                        # Ignore empty list items.
                        current_list.append_paragraph(new_p)
                else:
                    unordered_list: UnorderedList = UnorderedList()
                    if new_p:
                        unordered_list.append_paragraph(new_p)
                    new_text_elements.append(unordered_list)
                last_was_list = True
            for child in p.GetChildren():
                if isinstance(child, rt.RichTextField):
                    last_was_paragraph = False
                    last_was_list = False
                    field_type: str = child.GetProperties().GetProperty(Strings.field_type)
                    if field_type == Strings.field_image:
                        new_text_elements.append(self._doc.find_in_text_image(child.GetFieldType()))
                    else:
                        new_text_elements.append(self._doc.find_video(child.GetFieldType()))
        self._doc.set_text_elements(new_text_elements)

    def _convert_heading(self, p: rt.RichTextParagraph) -> Heading:
        """
        Create a heading instance from a RichTextParagraph.
        :param p: The RichTextParagraph.
        :return: A Heading instance.
        """
        child: rt.RichTextPlainText = p.GetChild(0)
        attrs: rt.RichTextAttr = child.GetAttributes()
        text: str = child.GetText()
        color: str = self._css_document.translate_color_str(attrs.GetTextColour())
        size: int = Heading.SIZE_H3 if attrs.GetFontFaceName() == Strings.style_heading_3 else Heading.SIZE_H4
        # Create the Heading instance.
        # Headings are never explicitly bold.
        return Heading(Text(text=text, bold=False, color=color), size)

    def _convert_paragraph(self, p: rt.RichTextParagraph):
        """
        Create a paragraph instance from a RichTextParagraph.
        :param p: The RichTextParagraph.
        :return: A Paragraph instance.
        """
        if p.GetChildCount() == 1:
            if not p.GetChild(0).GetText():
                # Empty paragraphs are considered empty lines and html paragraph ends. Return None as a special
                # delimiter which marks where to join paragraphs.
                return None

        # A paragraph consists of a list of instances of Text, Break and Link. Breaks are added above when paragraphs
        # are joined together.
        new_paragraph = Paragraph()
        for child in p.GetChildren():
            child: rt.RichTextPlainText
            attrs: rt.RichTextAttr = child.GetAttributes()

            text: str = child.GetText()
            bold: bool = False
            if attrs.GetFontWeight() == wx.FONTWEIGHT_BOLD:
                bold = True
            color = None
            # Color is irrelevant for links.
            if not attrs.HasURL():
                color = self._css_document.translate_color_str(attrs.GetTextColour())

            if attrs.HasURL():
                # This will be a link
                stored_link: Link = self._doc.find_link(attrs.GetURL())
                if not stored_link:
                    # There is a red unfinished link in the document, save it but keep it incorrect and turn the
                    # document red.
                    stored_link = Link(text, attrs.GetURL(), text, self._doc.get_other_articles(),
                                       self._doc.get_working_directory())
                    stored_link.test_self(self._config_manager.get_online_test())
                    self._doc.add_link(stored_link)
                # Update the text of the link from the current document.
                stored_link.set_text(text)
                new_paragraph.add_element(stored_link)
            else:
                # Ordinary text
                new_paragraph.add_element(Text(text, bold, color))
        return new_paragraph
