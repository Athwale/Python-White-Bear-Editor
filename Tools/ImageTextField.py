import wx
from wx.richtext import RichTextField, RichTextCtrl, RichTextBuffer, RichTextFieldTypeStandard

from Constants.Constants import Strings
from Gui.Dialogs.EditTextImageDialog import EditTextImageDialog
from Gui.Dialogs.EditVideoDialog import EditVideoDialog
from Tools.Document.ArticleElements.ImageInText import ImageInText


class ImageTextField(RichTextFieldTypeStandard):
    """
    Custom RichTextFieldType class with image edit dialog.
    """

    def __init__(self, element, working_dir: str):
        """
        Constructor for a custom label for displaying images with ability to edit.
        :param element: The Video or ImageInText instance to display.
        :param working_dir: Working directory of the editor
        """
        self._work_dir = working_dir
        self._element = element
        super().__init__(element.get_id(), bitmap=wx.Bitmap(element.get_image()),
                         displayStyle=RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)
        self.SetBorderColour(self._element.get_status_color())

    def CanEditProperties(self, obj: RichTextField) -> bool:
        """
        Rerun True if the user can edit the label's properties.
        :param obj: Unused
        :return: True
        """
        return True

    def GetPropertiesMenuLabel(self, obj: RichTextField) -> str:
        """
        Returns the label to be used for the properties' context menu item.
        :param obj: Unused
        :return: Label for the context menu.
        """
        if isinstance(self._element, ImageInText):
            return Strings.label_dialog_edit_image
        return Strings.label_dialog_edit_video

    def EditProperties(self, obj: RichTextField, parent: RichTextCtrl, buffer: RichTextBuffer) -> bool:
        """
        Edits the object's properties via a GUI.
        :param obj: The RichTextField object that has been clicked.
        :param parent: RichTextControl which contains the field.
        :param buffer: The buffer of the control.
        :return: The result of the GUI dialog.
        """
        if isinstance(self._element, ImageInText):
            edit_dialog = EditTextImageDialog(parent, self._element, self._work_dir)
        else:
            edit_dialog = EditVideoDialog(parent, self._element)

        result = edit_dialog.ShowModal()
        if result == wx.ID_OK:
            # Send an event to the main gui to signal document color change
            color_evt = wx.CommandEvent(wx.wxEVT_COLOUR_CHANGED, parent.GetId())
            color_evt.SetEventObject(self)
            wx.PostEvent(parent.GetEventHandler(), color_evt)
        edit_dialog.Destroy()

        self.SetBorderColour(self._element.get_status_color())
        self.SetBitmap(wx.Bitmap(self._element.get_image()))
        return result
