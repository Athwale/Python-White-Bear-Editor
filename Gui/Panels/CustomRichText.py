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

    def __init__(self, style_control: rt.RichTextStyleComboCtrl, parent, style):
        """
        Constructor for the custom rich text control.
        :param style_control: Style control from gui.
        :param parent: Parent of this control.
        :param style: wx style attributes.
        """
        super().__init__(parent, -1, style=style)
        self._parent = parent
        self._stylesheet = rt.RichTextStyleSheet()
        self._stylesheet.SetName('Stylesheet')
        self._style_control = style_control
        self._document = None

        self._create_styles()
        self._add_text_handlers()

        main_frame = wx.GetTopLevelParent(self)
        self.Bind(wx.EVT_KEY_UP, self.on_keypress)
        self.Bind(wx.EVT_TEXT_URL, self.url_in_text_click_handler, self)
        self.Bind(wx.EVT_MENU, self.on_insert_image, main_frame.edit_menu_item_insert_img)
        self.Bind(wx.EVT_MENU, self.on_insert_link, main_frame.edit_menu_item_insert_link)
        self.Bind(wx.EVT_MENU, self.on_insert_image, main_frame.insert_img_tool)
        self.Bind(wx.EVT_MENU, self.on_insert_link, main_frame.insert_link_tool)
        self.Bind(wx.EVT_MENU, self.on_bold, main_frame.bold_tool)

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
        # Normal style
        stl_paragraph: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_paragraph.SetParagraphSpacingBefore(Numbers.paragraph_spacing/2)
        stl_paragraph.SetParagraphSpacingAfter(Numbers.paragraph_spacing/2)
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph)
        self.ApplyStyle(style_paragraph)
        self.SetDefaultStyle(stl_paragraph)

        # Heading 3 style
        stl_heading_3: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_heading_3.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_3.SetFontWeight(wx.BOLD)
        stl_heading_3.SetFontSize(Numbers.heading_3_size)
        stl_heading_3.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        style_h3: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_3)
        style_h3.SetStyle(stl_heading_3)
        style_h3.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h3)

        # Heading 4 style
        stl_heading_4: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_heading_4.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_4.SetFontWeight(wx.BOLD)
        stl_heading_4.SetFontSize(Numbers.heading_4_size)
        stl_heading_4.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        style_h4: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading_4)
        style_h4.SetStyle(stl_heading_4)
        style_h4.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h4)

        # List style
        stl_list: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetParagraphSpacingAfter(Numbers.list_spacing)
        stl_list.SetParagraphSpacingBefore(Numbers.list_spacing)
        stl_list_1: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_list_1.SetBulletStyle(wx.TEXT_ATTR_BULLET_STYLE_STANDARD)
        stl_list_1.SetLeftIndent(Numbers.list_left_indent, Numbers.list_left_subindent)

        style_list: rt.RichTextListStyleDefinition = rt.RichTextListStyleDefinition(Strings.style_list)
        style_list.SetLevelAttributes(0, stl_list_1)
        style_list.SetStyle(stl_list)
        style_list.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_list)

        # Image style
        stl_image: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_image.SetAlignment(wx.TEXT_ALIGNMENT_CENTER)
        stl_image.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        stl_image.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
        style_image: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_image)
        style_image.SetStyle(stl_image)
        style_image.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_image)

        # Link style
        stl_link = rt.RichTextAttr()
        stl_link.SetFlags(wx.TEXT_ATTR_URL)
        stl_link.SetFontUnderlined(True)
        stl_link.SetTextColour(wx.BLUE)
        style_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition(Strings.style_url)
        style_link.SetStyle(stl_link)
        self._stylesheet.AddCharacterStyle(style_link)

        # Error Link style
        stl_error_link = rt.RichTextAttr()
        stl_error_link.SetFlags(wx.TEXT_ATTR_URL)
        stl_error_link.SetFontUnderlined(True)
        stl_error_link.SetBackgroundColour(wx.RED)
        style_error_link: rt.RichTextCharacterStyleDefinition = rt.RichTextCharacterStyleDefinition(
            Strings.style_error_url)
        style_error_link.SetStyle(stl_error_link)
        self._stylesheet.AddCharacterStyle(style_error_link)

        self.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()

    def set_content(self, doc: WhitebearDocumentArticle) -> None:
        """
        Set the document this text area is displaying.
        :param doc: The white bear article.
        :return: None
        """
        self.Clear()
        self.SetDefaultStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph).GetStyle())
        self._document = doc
        self.GetBuffer().CleanUpFieldTypes()
        for element in doc.get_main_text_elements():
            if isinstance(element, Paragraph):
                self._write_paragraph(element)
            elif isinstance(element, Heading):
                self._write_heading(element)
            elif isinstance(element, ImageInText):
                self._write_field(element.get_thumbnail_image_path(), element.get_image())
            elif isinstance(element, UnorderedList):
                self._write_list(element)
            elif isinstance(element, Video):
                self._write_field(element.get_url(), element.get_image())

    def _write_list(self, ul: UnorderedList) -> None:
        """
        Write an UnorderedList into the text area.
        :param ul: The list that will be on the field.
        :return: None
        """
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_list))
        self.BeginParagraphStyle(Strings.style_list)
        for li in ul.get_paragraphs():
            for element in li.get_elements():
                self._write_text(element)
            self.WriteText('\n')
        self.EndParagraphStyle()
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))

    def _write_field(self, path: str, image: wx.Image) -> None:
        """
        Write an ImageInText or Video into the text area.
        :param path: An identifying string either disk path or url.
        :param image: The image that will be on the field.
        :return: None
        """
        self._register_field(path, image)
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_image))
        self.BeginParagraphStyle(Strings.style_image)
        field = self.WriteField(path, rt.RichTextProperties())
        field.SetName(path)
        self.WriteText('\n')
        self.EndParagraphStyle()
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
        # TODO edit image on right click
        # TODo edit video on right click

    def _register_field(self, path: str, image: wx.Image) -> None:
        """
        Register a new custom field that represent an image.
        :param path: The full disk path of the image.
        :param image: The image to display.
        :return: None
        """
        self.field_type = ImageTextField(path, bitmap=wx.Bitmap(image),
                                         display_style=rt.RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)
        rt.RichTextBuffer.AddFieldType(self.field_type)

    def _write_heading(self, h: Heading) -> None:
        """
        Write a Heading into the text area.
        :param h: A Heading instance.
        :return: None
        """
        attr = wx.TextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if h.get_size() == Heading.SIZE_H3:
            style = Strings.style_heading_3
        else:
            style = Strings.style_heading_4
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(style))
        self.BeginParagraphStyle(style)
        self._write_text(h.get_text())
        self.EndParagraphStyle()
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
        self.Newline()

    def _write_paragraph(self, p: Paragraph) -> None:
        """
        Write a Paragraph into the text area.
        :param p: A Paragraph instance.
        :return: None
        """
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
        self.BeginParagraphStyle(Strings.style_paragraph)
        attr = wx.TextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        for element in p.get_elements():
            self._write_text(element)
        self.EndParagraphStyle()
        self.Newline()

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
            self.LineBreak()
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
        if color == wx.RED:
            self.BeginStyle(self._stylesheet.FindCharacterStyle(Strings.style_error_url).GetStyle())
        else:
            self.BeginStyle(self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle())
        self.BeginURL(link_id)
        self.WriteText(text)
        self.EndURL()
        self.EndStyle()
        self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))

    def on_insert_link(self, evt: wx.CommandEvent) -> None:
        """
        Insert a url link in the current position.
        :param evt: Unused,
        :return: None
        """
        new_link = Link("", Strings.link_stub, "", self._document.get_other_articles(),
                        self._document.get_working_directory())
        new_link.seo_test_self()
        edit_dialog = EditLinkDialog(self, new_link)
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            self._handle_link_edit(new_link)
        edit_dialog.Destroy()

    def url_in_text_click_handler(self, evt: wx.TextUrlEvent) -> None:
        """
        Handles click on url links inside text.
        :param evt: Not used
        :return: None
        """
        link = self._document.find_link(evt.GetString())
        link_text = self.GetRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
        link.set_text(link_text)
        edit_dialog = EditLinkDialog(self, link)
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            self._handle_link_edit(link, evt)
        edit_dialog.Destroy()

    def _handle_link_edit(self, link: Link, evt: wx.TextUrlEvent = None) -> None:
        """
        Handle actions needed after a link has been edited in the link edit dialog.
        :param link: The modified Link instance
        :param evt: If an event is passed in it is used to find where to replace the link, otherwise the link is
        inserted into the current position.
        :return: None
        """
        # TODO set document modified only if an edit has been made in the dialog
        self._document.set_modified(True)
        self._document.add_link(link)
        if evt:
            # Replace an existing link
            self.Remove(evt.GetURLStart(), evt.GetURLEnd() + 1)
        self._insert_link(link.get_text()[0], link.get_id(), link.get_status_color())
        # Send an event to the main gui to signal document color change
        color_evt = wx.CommandEvent(wx.wxEVT_COLOUR_CHANGED, self.GetId())
        color_evt.SetEventObject(self)
        wx.PostEvent(self.GetEventHandler(), color_evt)

    def on_insert_image(self, evt):
        # TODO this.
        field = self.WriteField('imageFieldType', rt.RichTextProperties())
        field.SetName('image1')

    def on_bold(self, evt) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        self.ApplyBoldToSelection()

    def _get_style_at_pos(self, position: int = 0) -> (str, bool):
        """
        Get the style name at given position in the text. 0 - current position, -1 - before current position
        1 - after current position.
        :param position: The position.
        :return: Style name.
        """
        style_carrier = rt.RichTextAttr()
        self.GetStyle(position, style_carrier)
        return style_carrier.GetParagraphStyleName(), style_carrier.HasURL()

    def on_keypress(self, event):
        """

        :param event:
        :return:
        """
        current_style = self._stylesheet.FindParagraphStyle(Strings.style_paragraph).GetStyle().GetParagraphStyleName()
        current_position = self.GetCaretPosition()
        print('pos: ' + str(current_position))
        print('previous: ' + str(
            str(self._get_style_at_pos(current_position - 1)) + ' ' + self.GetRange(current_position - 1,
                                                                                    current_position)))
        print('current: ' + str(
            str(self._get_style_at_pos(current_position + 1)) + ' ' + self.GetRange(current_position,
                                                                                    current_position + 1)))
        print('next: ' + str(
            str(self._get_style_at_pos(current_position + 2)) + ' ' + self.GetRange(current_position + 1,
                                                                                    current_position + 2)))

        print(self._get_style_at_pos(0) == current_style)
        event.Skip()
