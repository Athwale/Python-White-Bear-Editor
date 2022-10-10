
import wx
import wx.richtext as rt
from wx.richtext import RichTextField, RichTextCtrl, RichTextBuffer, RichTextFieldTypeStandard


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self._button = wx.Button(self, wx.ID_APPLY, 'Select image')
        self.Bind(wx.EVT_BUTTON, self.pick_image_handler, self._button)
        self.sizer.Add(self._button)
        self.SetSizer(self.sizer)

    # noinspection PyUnusedLocal
    def pick_image_handler(self, event: wx.CommandEvent) -> str:
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
        return image_path

    def process_image(self, img_path: str) -> None:
        """
        Process a logo.
        :param img_path: Path to an image.
        :return: None
        """
        def find_image():
            for y in range(0, image.GetHeight()):
                for x in range(0, image.GetWidth()):
                    color = image.GetRed(x, y)
                    image.SetRGB(x, y, 255, 0, 0)
                    print(color)
                    if color != 255:
                        return x, y

        image = wx.Image(img_path)
        image: wx.Image = image.ConvertToGreyscale()

        print(find_image())

        bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(image))
        self.sizer.Add(bitmap)


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(400, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.process_image('/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Experiments/Screenshot.png')
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
