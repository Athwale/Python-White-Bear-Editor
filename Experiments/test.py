import wx
import wx.richtext as rt

from wx.richtext import RichTextField, RichTextFieldTypeStandard


class RichTextFrame(wx.Frame):

    # Used for image differentiation.
    id = 1

    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._main_sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.SetSizer(self._main_sizer)

        self.rtc.GetBuffer().CleanUpFieldTypes()

    def write_field(self) -> None:
        """
        Write an image field into the text area.
        :return: None
        """
        new_field = self._register_field()
        self.rtc.WriteField(new_field.GetName(), rt.RichTextProperties())
        print(new_field.GetName())

    @staticmethod
    def _register_field():
        """
        Register a new custom image field.
        :return: None
        """
        # Create unique id for the image.
        RichTextFrame.id = RichTextFrame.id + 1

        # Create a sample image for the field.
        dc = wx.MemoryDC()
        font: wx.Font = dc.GetFont()
        font.SetPointSize(16)
        dc.SetFont(font)
        size = dc.GetTextExtent('Field: ' + str(RichTextFrame.id))
        bitmap = wx.Bitmap(width=size[0] + 10, height=size[1] + 10)
        dc.SelectObject(bitmap)
        dc.Clear()
        dc.SetTextForeground(wx.BLACK)
        dc.DrawText('Field: ' + str(RichTextFrame.id), 5, 5)

        field_type = ImageTextField(str(RichTextFrame.id), bitmap)
        rt.RichTextBuffer.AddFieldType(field_type)
        return field_type


class ImageTextField(RichTextFieldTypeStandard):
    """
    Custom RichTextFieldType class with an image.
    """

    def __init__(self, field_id: str, img: wx.Bitmap):
        """
        Constructor for a custom label for displaying images.
        """
        super().__init__(field_id, bitmap=img, displayStyle=RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)

    def CanEditProperties(self, obj: RichTextField) -> bool:
        return False


class MyApp(wx.App):
    """
    Main class for running the gui.
    """
    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(300, 300), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.write_field()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
