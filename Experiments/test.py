import wx

from Constants.Constants import Numbers


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self._button = wx.Button(self, wx.ID_APPLY, 'Select image')
        self.Bind(wx.EVT_BUTTON, self.pick_image_handler, self._button)
        self.sizer.Add(self._button, flag=wx.EXPAND, proportion=0)
        self.SetSizer(self.sizer)

    # noinspection PyUnusedLocal
    def pick_image_handler(self, event: wx.CommandEvent) -> None:
        """
        Open a file dialog to select an image.
        :param event: Not used.
        :return: None
        """
        image_path = ''
        with wx.FileDialog(self, 'Select image', '.', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dlg: wx.FileDialog
                image_path = dlg.GetPath()
                self.process_image(image_path)

    def process_image(self, img_path: str) -> None:
        """
        Process a logo.
        :param img_path: Path to an image.
        :return: None
        """
        image = wx.Image(img_path)
        image: wx.Image = image.ConvertToGreyscale()

        # TODO https://discuss.wxpython.org/t/cropping-an-image-with-wxpython/34983/6
        # TODO make threshold user selectable
        # TODO make border selectable by user
        # TODO try big, small, completely white, tall, short images
        # TODO create logo name based on article name not filename.
        images = self.prepare_image(image, limit=183, border=6)
        if images:
            for img in images:
                bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(img))
                self.sizer.Add(wx.StaticLine(self, -1))
                self.sizer.Add(bitmap)
        self.sizer.Layout()

    @staticmethod
    def prepare_image(image: wx.Image, limit: int, border: int) -> (wx.Image, wx.Image):
        """
        Search for the beginning of an image based on red color threshold from the set direction.
        :param image: The logo to process.
        :param limit: The red color threshold where we consider the image to be useful.
        :param border: How many white pixels to put around the image.
        :return: 2 images - preview and finished logo.
        """
        # Bounding box will be drawn only into the preview.
        preview = image.Copy()
        # Top will be set only once on the first matching pixel.
        top = None
        # Bottom is the last matching pixel.
        bottom = None
        # Left will be gradually adjusted to the leftmost smallest x coordinate.
        left = (image.GetWidth(), 0)
        # Right will be gradually adjusted to the rightmost highest x coordinate.
        right = (0, 0)
        for y in range(0, image.GetHeight() - 1):
            for x in range(0, image.GetWidth() - 1):
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
                    preview.SetRGB(x, y, 255, 255, 255)
                    image.SetRGB(x, y, 255, 255, 255)

        if top is None or bottom is None:
            return

        top_left = (left[0], top[1])
        bottom_right = (right[0], bottom[1])

        # Draw a bounding box around the selected area.
        for y in range(0, preview.GetHeight() - 1):
            for x in range(0, preview.GetWidth() - 1):
                if x == top_left[0] or x == bottom_right[0]\
                        or y == top_left[1] or y == bottom_right[1]:
                    preview.SetRGB(x, y, 255, 0, 0)
        # Get only the selected part of the image.
        crop: wx.Image = image.GetSubImage(wx.Rect(wx.Point(top_left), wx.Point(bottom_right)))
        # Rescale it to fit into the logo size - border and respect aspect ratio
        width_scale = Numbers.menu_logo_image_size / crop.GetWidth()
        height_scale = Numbers.menu_logo_image_size / crop.GetHeight()
        bounded_scale = min(width_scale, height_scale)
        crop.Rescale(width=int(crop.GetWidth() * bounded_scale) - border,
                     height=int(crop.GetHeight() * bounded_scale) - border,
                     quality=wx.IMAGE_QUALITY_HIGH)
        # TODO the size here must not be more than 96, how do you make it fit?
        # TODO make the larger side 96 then find out by how much the other side is out of bounds?
        logo_size = (Numbers.menu_logo_image_size, Numbers.menu_logo_image_size)
        position = (int(border / 2), int(border / 2))
        # Place the small logo into the middle of the final correctly sized image with white background.
        crop.Resize(logo_size, position, 255, 255, 255)
        return preview, crop


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(300, 600), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
