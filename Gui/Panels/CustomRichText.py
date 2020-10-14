from typing import List, Dict

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

        self.register_field()
        # self.insert_sample_text()

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
        stl_paragraph.SetParagraphSpacingAfter(20)
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_paragraph)
        self.ApplyStyle(style_paragraph)
        self.SetDefaultStyle(stl_paragraph)

        # Heading style
        stl_heading_3: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_heading_3.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_heading_3.SetFontWeight(wx.BOLD)
        stl_heading_3.SetFontSize(Numbers.heading_1_size)
        stl_heading_3.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        style_h3: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_heading)
        style_h3.SetStyle(stl_heading_3)
        style_h3.SetNextStyle(Strings.style_paragraph)
        self._stylesheet.AddParagraphStyle(style_h3)

        # List style
        stl_list: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_list.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_list.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        stl_list.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
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

        self.SetStyleSheet(self._stylesheet)
        self._style_control.SetRichTextCtrl(self)
        self._style_control.SetStyleSheet(self._stylesheet)
        self._style_control.UpdateStyles()

    def set_content(self, doc: WhitebearDocumentArticle) -> None:
        """
        Set the document this text area is displaying.
        :param doc: The white bear article.
        :param colors: The parses css colors.
        :return: None
        """
        self.Clear()
        self._document = doc
        for element in doc.get_main_text_elements():
            if isinstance(element, Paragraph):
                self._write_paragraph(element)
            elif isinstance(element, Heading):
                print('heading')
            elif isinstance(element, ImageInText):
                print('image')
            elif isinstance(element, UnorderedList):
                print('list')
            elif isinstance(element, Video):
                print('video')

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
            if isinstance(element, Text):
                self.BeginTextColour(element.get_color())
                self.WriteText(element.get_text())
                self.EndTextColour()
            elif isinstance(element, Break):
                self.LineBreak()
            elif isinstance(element, Link):
                print('link')

        self.EndParagraphStyle()
        self.Newline()


    def url_in_text_click_handler(self, evt) -> None:
        """
        Handles click on url links inside text.
        :param evt: Not used
        :return: None
        """
        link = self.GetRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
        wx.MessageBox(evt.GetString() + ' ' + link, "URL Clicked")

    def on_insert_image(self, evt):
        # TODO this.
        field = self.WriteField('imageFieldType', rt.RichTextProperties())
        field.SetName('image1')

    def on_insert_link(self, evt: wx.CommandEvent) -> None:
        """
        Insert a url link in the current position.
        :param evt: Unused,
        :return: None
        """
        edit_dialog = EditLinkDialog(self)
        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            # TODO set document modified if an edit has been made in the dialog
            # TODO change the link in the editor
            print('Ok')
        edit_dialog.Destroy()
        self.insert_link('www.google.com', 'google')

    def insert_link(self, url: str, text: str) -> None:
        """
        Insert a link into text at current position.
        :param url: The url behind the link
        :param text: The visible text.
        :return: None
        """
        self.BeginStyle(self._stylesheet.FindCharacterStyle(Strings.style_url).GetStyle())
        self.BeginURL(url)
        self.WriteText(text)
        self.EndURL()
        self.EndStyle()
        # TODO edit link in place (create a link edit dialog)

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

    def register_field(self) -> None:
        # TODO use this to make images in text
        self.field_type = ImageTextField('imageFieldType', bitmap=wx.Bitmap(
            wx.Image('/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Resources/main_image_missing.png',
                     wx.BITMAP_TYPE_PNG)), display_style=rt.RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)
        rt.RichTextBuffer.AddFieldType(self.field_type)

    def insert_sample_text(self) -> None:
        if True:
            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
            self.BeginParagraphStyle(Strings.style_paragraph)
            self.WriteText('paragraph1')
            self.EndParagraphStyle()

            self.Newline()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_heading))
            self.BeginParagraphStyle(Strings.style_heading)
            self.WriteText('Heading3')
            self.EndParagraphStyle()

            self.Newline()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
            self.BeginParagraphStyle(Strings.style_paragraph)
            self.WriteText('paragraph2')
            self.EndParagraphStyle()

            self.Newline()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_list))
            self.BeginParagraphStyle(Strings.style_list)
            self.WriteText('List item 1\n')
            self.WriteText('List item 2\n')
            self.WriteText('List item 3\n')
            self.EndParagraphStyle()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
            self.BeginParagraphStyle(Strings.style_paragraph)
            self.WriteText('paragraph4')
            self.EndParagraphStyle()

            self.Newline()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_image))
            self.BeginParagraphStyle(Strings.style_image)
            field = self.WriteField('imageFieldType', rt.RichTextProperties())
            field.SetName('image1')
            self.WriteText('\n')
            self.EndParagraphStyle()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
            self.BeginParagraphStyle(Strings.style_paragraph)
            self.WriteText('paragraph5 sample of a longer text for testing url creation ')
            self.insert_link('www.seznam.cz', 'link from code')
            self.EndParagraphStyle()

            self.Newline()

            self.ApplyStyle(self._stylesheet.FindParagraphStyle(Strings.style_paragraph))
            self.BeginParagraphStyle(Strings.style_paragraph)
            self.insert_link('www.seznam.cz', 'link from code')
            self.EndParagraphStyle()