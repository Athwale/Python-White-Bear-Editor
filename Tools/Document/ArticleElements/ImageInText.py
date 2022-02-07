import os

import wx

from Constants.Constants import Numbers
from Resources.Fetch import Fetch
from Tools.Document.BaseImage import BaseImage


class ImageInText(BaseImage):
    """
    Carrier class for a parsed in text image.
    """

    def __init__(self, title: str, image_alt: str, original_image_path: str, thumbnail_path: str,
                 full_filename: str, thumbnail_filename: str):
        """
        Constructor for an image that is inside text.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param original_image_path: full disk path to the original size image.
        :param thumbnail_path: full path to the thumbnail image.
        :param full_filename: file name of the full image
        :param thumbnail_filename: file name of the thumbnail image
        """
        super().__init__(title, image_alt, original_image_path, thumbnail_path, full_filename, thumbnail_filename)

    def copy(self):
        """
        Returns a copy of this image.
        :return: A copy of this image.
        """
        return ImageInText(self.get_link_title()[0], self.get_image_alt()[0], self.get_original_image_path(),
                           self.get_thumbnail_image_path(), self.get_full_filename(), self.get_thumbnail_filename())

    def test_self(self) -> bool:
        """
        SEO test self for alt and link title. If the image and thumbnail is not accessible on disk, set a
        special warning image.
        :return: True if test is ok, False otherwise
        """
        # First test the base class seo attributes
        result = super(ImageInText, self).test_self()

        # Check thumbnail image disk path
        if not self._thumbnail_path or not os.path.exists(self._thumbnail_path):
            # The image has generic text and can be reused.
            self._image = wx.Image(Fetch.get_resource_path('main_image_thumbnail_missing.png'), wx.BITMAP_TYPE_PNG)
            self._thumbnail_size = (0, 0)
            result = False
        else:
            # Image thumbnails in text must not be larger than 534 px.
            image = wx.Image(Fetch.get_resource_path(self._thumbnail_path), wx.BITMAP_TYPE_ANY)
            self._thumbnail_size = image.GetSize()
            if self._thumbnail_size[0] <= Numbers.text_image_max_size \
                    and self._thumbnail_size[1] <= Numbers.text_image_max_size:
                self._image = image
            else:
                self._image = wx.Image(Fetch.get_resource_path('main_image_thumbnail_wrong.png'), wx.BITMAP_TYPE_PNG)
                self._thumbnail_size = self._image.GetSize()
                result = False

            # Check full image disk path, size can be whatever the user likes
            if not self._original_image_path or not os.path.exists(self._original_image_path):
                self._image = wx.Image(Fetch.get_resource_path('main_image_missing.png'), wx.BITMAP_TYPE_PNG)
                result = False

        if not result:
            self._status_color = wx.RED
        return result

    def __str__(self) -> str:
        return "Text image: id: {}, original: {}, thumbnail: {}, title: {}, alt: {}".format(self._image_id,
                                                                                            self._original_image_path,
                                                                                            self._thumbnail_path,
                                                                                            self._link_title,
                                                                                            self._image_alt)
