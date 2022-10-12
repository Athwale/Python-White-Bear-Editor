
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
        def find_image(limit: int) -> (int, int):
            """
            Search for the beginning of an image based on red color threshold from the set direction.
            :param limit: The red color threshold where we consider the image to be useful.
            :return: Found coordinates.
            """
            # TODO make threshold user selectable
            # todo do it all in one go?
            # todo rewrite to white below threshold.
            y_range = range(0, image.GetHeight() - 1)
            x_range = range(0, image.GetWidth() - 1)
            # Top will be set only once on the first matching pixel.
            top = None
            # Left will be gradually adjusted to the leftmost smallest x coordinate.
            left = (image.GetWidth(), 0)
            # Right will be gradually adjusted to the rightmost highest x coordinate.
            right = (0, 0)
            # Bottom is the last matching pixel.
            bottom = None
            for y in y_range:
                for x in x_range:
                    color = image.GetRed(x, y)
                    # A shade of gray that we consider gray enough to count as the image we want.
                    if color < limit:
                        if not top:
                            top = (x, y)
                        if x < left[0]:
                            left = (x, y)
                        if x > right[0]:
                            right = (x, y)
                        else:
                            bottom = (x, y)
                    else:
                        # Repaint all lighter colors with white
                        image.SetRGB(x, y, 255, 255, 255)

            print('top', top)
            print('left', left)
            print('right', right)
            print('bottom', bottom)
            for b in (top, left, right, bottom):
                image.SetRGB(b[0], b[1], 255, 0, 0)

        image = wx.Image(img_path)
        image: wx.Image = image.ConvertToGreyscale()

        print(find_image(limit=183))

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
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(300, 300), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.process_image('/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Experiments/Screenshot.png')
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
