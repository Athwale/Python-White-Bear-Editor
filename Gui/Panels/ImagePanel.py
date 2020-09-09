import wx

from Constants.Constants import Strings
from Constants.Constants import Numbers
from Tools.Document.AsideImage import AsideImage


class ImagePanel(wx.Panel):
    """

    """

    def __init__(self, *args, **kw):
        """
        Constructor for the image panel.
        """
        super().__init__(*args, **kw)
        self._image = None

        # Create layout
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
        self._label = wx.StaticText(self, -1, Strings.lable_image)
        self._sizer.Add(self._bitmap)
        self._sizer.Add(self._label)
        self._sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        self.SetSizer(self._sizer)
        self.Layout()

    def set_image(self, image: AsideImage) -> None:
        """
        Set a new image into this panel.
        :param image: The image to set.
        :return: None
        """
        self._image = image
        self._label.SetLabelText(self._image.get_image_caption()[0])
        self._bitmap.SetBitmap(wx.Bitmap(self._image.get_image()))
        self.Layout()
