
import wx
import wx.richtext as rt
from wx.richtext import RichTextField, RichTextCtrl, RichTextBuffer, RichTextFieldTypeStandard


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self._button = wx.Button(self, wx.ID_APPLY, 'Img')
        self.Bind(wx.EVT_BUTTON, self.insert_image, self._button)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.sizer.Add(self._button)
        self.SetSizer(self.sizer)

    def insert_image(self, event: wx.CommandEvent) -> None:
        """
        Open a file dialog to insert an image.
        :param event: Not used.
        :return: None
        """
        image_path = ''
        with wx.FileDialog(self, 'Select image', '.', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                image_path = dlg.GetPath()

        field_type = ImageTextField(image_path)
        rt.RichTextBuffer.AddFieldType(field_type)

        position = self.rtc.GetAdjustedCaretPosition(self.rtc.GetCaretPosition())
        buffer: rt.RichTextBuffer = self.rtc.GetFocusObject()
        buffer.InsertFieldWithUndo(self.rtc.GetBuffer(), position, field_type.GetName(), rt.RichTextProperties(),
                                   self.rtc, rt.RICHTEXT_INSERT_NONE, rt.RichTextAttr())


class ImageTextField(RichTextFieldTypeStandard):
    """
    Custom RichTextFieldType class with image edit dialog.
    """

    def __init__(self, img_path: str):
        """
        Constructor for a custom label for displaying images with ability to edit.
        :param img_path: Path to image.
        """
        self._img = img_path
        super().__init__('1', bitmap=wx.Bitmap(wx.Image(img_path, wx.BITMAP_TYPE_ANY)),
                         displayStyle=RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)
        self.SetBorderColour(wx.RED)

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
        return 'Edit image'

    def EditProperties(self, obj: RichTextField, parent: RichTextCtrl, buffer: RichTextBuffer) -> None:
        """
        Edits the object's properties via a GUI.
        :param obj: The RichTextField object that has been clicked.
        :param parent: RichTextControl which contains the field.
        :param buffer: The buffer of the control.
        :return: The result of the GUI dialog.
        """
        image_path = ''
        with wx.FileDialog(parent, 'Select img', '.', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                image_path = dlg.GetPath()
        self.update_image(image_path)
        parent.Refresh()

    def update_image(self, img_path: str) -> None:
        """
        Redraw the image according to the seo status.
        :param img_path: Path to image.
        :return: None
        """
        # TODO changing the image size to a smaller image does not change the label size
        self.SetBorderColour(wx.BLUE)
        self.SetBitmap(wx.Bitmap(wx.Image(img_path, wx.BITMAP_TYPE_ANY)))


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
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
