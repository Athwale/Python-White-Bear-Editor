from typing import List

import wx
import wx.lib.scrolledpanel

from Constants.Constants import Numbers
from Tools.Document.AsideImage import AsideImage


class AsideImagePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """

    """

    def __init__(self, parent):
        """
        Constructor for the AsideImagePanel which has special functionality
        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1)
        self.images: List[AsideImage] = []
        self.bitmaps = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def add_image(self, image: AsideImage) -> None:
        """
        Add another image into this container panel.
        :param image: The wx.Image to add.
        :return: None
        """
        self.images.append(image)

    def clear_images(self) -> None:
        """
        Clear the list of images. This has to be done when switching to a different article.
        :return: None
        """
        self._clear_panel()
        self.images.clear()

    def _clear_panel(self) -> None:
        """
        Clear loaded bitmaps and free memory.
        :return: None
        """
        for child in self.GetChildren():
            child.Destroy()
        self.bitmaps.clear()

    def show_images(self) -> None:
        """
        Show the list of images on the panel.
        :return: None
        """
        self.Hide()
        # First clear already displayed images
        self._clear_panel()

        # Create and show new images
        for img in self.images:
            bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(img.get_image()))
            self.bitmaps.append(bitmap)
            self.sizer.Add(bitmap)
            self.sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))

        self.SetupScrolling(scroll_x=False, scrollIntoView=True)
        self.Layout()
        self.Show()


