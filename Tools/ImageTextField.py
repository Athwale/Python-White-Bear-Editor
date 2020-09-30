import wx
from wx.richtext import RichTextFieldTypeStandard, RichTextField, RichTextCtrl, RichTextBuffer

from Constants.Constants import Strings


class ImageTextField(RichTextFieldTypeStandard):
    """
    Custom RichTextFieldType class with image edit dialog.
    """

    def __init__(self, name, bitmap, display_style):
        """
        Constructor for a custom label for displaying images with ability to edit.
        """
        super().__init__(name, bitmap, display_style)

    def CanEditProperties(self, obj: RichTextField) -> bool:
        """
        Rerurn True if the user can edit the label's properties.
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
        wx.MessageBox(obj.GetName() + ' ' + " Clicked")
        return False
