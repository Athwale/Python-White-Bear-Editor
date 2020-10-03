import wx
import wx.richtext as rt

from Constants.Constants import Strings, Numbers
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle


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
        self.stylesheet = rt.RichTextStyleSheet()
        self.stylesheet.SetName('Stylesheet')
        self.style_control = style_control
        self.document = None

        self._create_styles()
        self._add_text_handlers()

        main_frame = wx.GetTopLevelParent(self)
        # TODO pick correct event, key down gets handled too early
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
        stl_paragraph.SetParagraphSpacingAfter(20)
        style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(
            Strings.style_paragraph)
        style_paragraph.SetStyle(stl_paragraph)
        style_paragraph.SetNextStyle(Strings.style_paragraph)
        self.stylesheet.AddParagraphStyle(style_paragraph)
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
        self.stylesheet.AddParagraphStyle(style_h3)

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
        self.stylesheet.AddParagraphStyle(style_list)

        # Image style
        stl_image: rt.RichTextAttr = self.GetDefaultStyleEx()
        stl_image.SetAlignment(wx.TEXT_ALIGNMENT_CENTER)
        stl_image.SetParagraphSpacingAfter(Numbers.paragraph_spacing)
        stl_image.SetParagraphSpacingBefore(Numbers.paragraph_spacing)
        style_image: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition(Strings.style_image)
        style_image.SetStyle(stl_image)
        style_image.SetNextStyle(Strings.style_paragraph)
        self.stylesheet.AddParagraphStyle(style_image)

        self.SetStyleSheet(self.stylesheet)
        self.style_control.SetRichTextCtrl(self)
        self.style_control.SetStyleSheet(self.stylesheet)
        self.style_control.UpdateStyles()

    def set_document(self, doc: WhitebearDocumentArticle) -> None:
        """
        Set which document this text area is displaying.
        :param doc: The white bear article.
        :return: None
        """
        self.document = doc

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

    def on_insert_link(self, evt):
        # TODO do something with this
        # TODO Try catching keypresses earlier and check style then replace this with a style
        # Url Style
        stl_url = self.GetDefaultStyleEx()
        stl_url.SetTextColour(wx.BLUE)
        stl_url.SetFontUnderlined(True)

        self.BeginStyle(stl_url)
        self.BeginURL('www.google.com')
        self.WriteText('google')
        self.EndURL()
        self.EndStyle()

    def on_bold(self, evt) -> None:
        """
        Make text bold and vice versa.
        :param evt: Not used
        :return: None
        """
        self.ApplyBoldToSelection()

    def _get_style_at_pos(self, position: int = 0) -> str:
        """
        Get the style name at given position in the text. 0 - current position, -1 - before current position
        1 - after current position.
        :param position: The position.
        :return: Style name.
        """
        style_carrier = rt.RichTextAttr()
        self.GetStyle(position, style_carrier)
        return style_carrier.GetParagraphStyleName()

    def on_keypress(self, event):
        # TODO how to tell we are at the end of a paragraph?
        # TODO bacha na to co znamnea predemnou, to je primo ta pozice kde stojim.
        current_style = self.stylesheet.FindParagraphStyle(Strings.style_paragraph).GetStyle().GetParagraphStyleName()
        current_positon = self.GetCaretPosition()
        print('pos: ' + str(current_positon))
        print('previous: ' + str(self._get_style_at_pos(current_positon - 1) + ' ' + self.GetRange(current_positon - 1, current_positon)))
        print('current: ' + str(self._get_style_at_pos(current_positon + 1) + ' ' + self.GetRange(current_positon, current_positon + 1)))
        print('next: ' + str(self._get_style_at_pos(current_positon + 2) + ' ' + self.GetRange(current_positon + 1, current_positon + 2)))

        print(self._get_style_at_pos(0) == current_style)
        event.Skip()
