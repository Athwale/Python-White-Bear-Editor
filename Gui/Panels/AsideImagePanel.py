from typing import List

import wx
import wx.lib.scrolledpanel

from Gui.Panels.ImagePanel import ImagePanel
from Tools.Document.AsideImage import AsideImage


class AsideImagePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """

    """

    def __init__(self, parent):
        """
        Constructor for the AsideImagePanel which has special functionality
        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1)
        self._images: List[AsideImage] = []
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

    def add_image(self, image: AsideImage) -> None:
        """
        Add another image into this container panel.
        :param image: The wx.Image to add.
        :return: None
        """
        self._images.append(image)

    def clear_images(self) -> None:
        """
        Clear the list of images. This has to be done when switching to a different article.
        :return: None
        """
        self._clear_panel()
        self._images.clear()

    def _clear_panel(self) -> None:
        """
        Clear loaded bitmaps and free memory.
        :return: None
        """
        for child in self.GetChildren():
            child.Destroy()

    def show_images(self) -> None:
        """
        Show the list of images on the panel.
        :return: None
        """
        self.Hide()
        # First clear already displayed images
        self._clear_panel()

        # Create and show new images
        for img in self._images:
            image_panel = ImagePanel(self)
            image_panel.set_image(img)
            self._sizer.Add(image_panel)

        self.SetupScrolling(scroll_x=False, scrollIntoView=True)
        self.Layout()
        self.Show()


