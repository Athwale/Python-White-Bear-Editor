import wx

from Constants.Constants import Strings
from Tools.Document.AsideImage import AsideImage


class EditImageDialog(wx.Dialog):

    def __init__(self, parent, image: AsideImage):
        """
        Display a modal dialog with a message with the text being selectable.
        :param parent: Parent frame.
        :param image: AsideImage instance being edited by tis dialog.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_image)
        self.image = image

        self.main_vertical_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetMinSize((410, 250))

        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.cancel_button.SetDefault()

        self.main_vertical_sizer.Add(self.cancel_button)
        self.main_vertical_sizer.Add(self.ok_button)
        self.SetSizer(self.main_vertical_sizer)
