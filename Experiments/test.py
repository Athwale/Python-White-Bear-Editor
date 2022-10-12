import wx


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self._button = wx.Button(self, wx.ID_APPLY, 'Select image')
        self.Bind(wx.EVT_BUTTON, self.pick_image_handler, self._button)
        self.sizer.Add(self._button, flag=wx.EXPAND, proportion=0)
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
        image = wx.Image(img_path)
        image: wx.Image = image.ConvertToGreyscale()
        bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(image))
        self.sizer.Add(bitmap)

        # TODO make threshold user selectable
        print(image.GetWidth(), image.GetHeight())
        logo = self.prepare_image(image, limit=183)
        bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(logo))
        self.sizer.Add(bitmap)
        self.sizer.Layout()

    def prepare_image(self, image: wx.Image, limit: int) -> wx.Image:
        """
        Search for the beginning of an image based on red color threshold from the set direction.
        :param image: The logo to process.
        :param limit: The red color threshold where we consider the image to be useful.
        :return: Found coordinates.
        """
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
                    image.SetRGB(x, y, 255, 255, 255)

        top_left = (left[0], top[1])
        bottom_right = (right[0], bottom[1])
        # TODO make a new blank image of the size of the selected area.
        logo = wx.Image(100, 100, clear=True)
        logo.Replace(0, 0, 0, 255, 255, 255)
        for y in range(0, image.GetHeight() - 1):
            for x in range(0, image.GetWidth() - 1):
                if x == top_left[0] or x == bottom_right[0]\
                        or y == top_left[1] or y == bottom_right[1]:
                    image.SetRGB(x, y, 255, 0, 0)
                if top_left[0] <= x <= bottom_right[0] and top_left[1] <= y <= bottom_right[1]:
                    # TODO Copy these pixels into a new image of appropriate size.
                    # TODO then resize it to less than 96 pixels and pad it to 96 with white?
                    print(x, y)

        return logo


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(300, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        self.frame.process_image('/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Experiments/Screenshot.png')
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
