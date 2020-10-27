import wx
from wx.richtext import RichTextField, RichTextCtrl, RichTextBuffer, RichTextFieldTypeStandard

from Constants.Constants import Strings
from Gui.Dialogs.EditTextImageDialog import EditTextImageDialog
from Gui.Dialogs.EditVideoDialog import EditVideoDialog
from Tools.Document.ArticleElements.ImageInText import ImageInText
from Tools.Document.ArticleElements.Video import Video


class ImageTextField(RichTextFieldTypeStandard):
    """
    Custom RichTextFieldType class with image edit dialog.
    """

    def __init__(self, element):
        """
        Constructor for a custom label for displaying images with ability to edit.
        :param element: The Video or ImageInText instance to display.
        """
        if isinstance(element, ImageInText):
            path = element.get_thumbnail_image_path()
            self._image: ImageInText = element
            self._video = None
        else:
            path = element.get_url()[0]
            self._video: Video = element
            self._image = None
        super().__init__(path, bitmap=wx.Bitmap(element.get_image()),
                         displayStyle=RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)

    def CanEditProperties(self, obj: RichTextField) -> bool:
        """
        Rerun True if the user can edit the label's properties.
        :param obj: Unused
        :return: True
        """
        return True

    def GetPropertiesMenuLabel(self, obj: RichTextField) -> str:
        """
        Returns the label to be used for the properties context menu item.
        :param obj: Unused
        :return: Label for the context menu.
        """
        return Strings.label_menu_edit_image

    def EditProperties(self, obj: RichTextField, parent: RichTextCtrl, buffer: RichTextBuffer) -> bool:
        """
        Edits the object's properties via a GUI.
        :param obj: The RichTextField object that has been clicked.
        :param parent: RichTextControl which contains the field.
        :param buffer: The buffer of the control.
        :return: The result of the GUI dialog.
        """
        if self._image:
            edit_dialog = EditTextImageDialog(parent, self._image)
        else:
            edit_dialog = EditVideoDialog(parent, self._video)

        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            # TODO set document modified if an edit has been made in the dialog
            print('Ok')
        edit_dialog.Destroy()
        return False
