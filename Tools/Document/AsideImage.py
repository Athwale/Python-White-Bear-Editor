import os

import wx

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Resources.Fetch import Fetch
from Tools.Document.BaseImage import BaseImage


class AsideImage(BaseImage):
    """
    Carrier class for a parsed aside image.
    """

    def __init__(self, section: str, caption: str, title: str, image_alt: str, original_image_path: str,
                 thumbnail_path: str, full_filename: str, thumbnail_filename: str):
        """
        Constructor for an aside image.
        :param section: The website section the image belongs to (elektronika,...)
        :param caption: Figcaption of the aside image.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param original_image_path: full disk path to the original size image.
        :param thumbnail_path: full path to the thumbnail image.
        :param full_filename: file name of the full image
        :param thumbnail_filename: file name of the thumbnail image
        """
        super().__init__(section, title, image_alt, original_image_path, thumbnail_path, full_filename,
                         thumbnail_filename)
        self._caption = caption
        self._caption_error_message: str = ''

    def copy(self):
        """
        Returns a copy of this image.
        :return: A copy of this image.
        """
        return AsideImage(self.get_section(), self.get_caption()[0], self.get_link_title()[0], self.get_image_alt()[0],
                          self.get_original_image_path(), self.get_thumbnail_image_path(), self.get_full_filename(),
                          self.get_thumbnail_filename())

    def seo_test_self(self) -> bool:
        """
        SEO test self for caption, alt and link title. If the image and thumbnail is not accessible on disk, set a
        special warning image.
        :return: True if test is ok, False otherwise
        """
        # Clear all error before each retest
        self._caption_error_message: str = ''

        # First test the base class seo attributes
        result = super(AsideImage, self).seo_test_self()

        # Check caption length must be at least 3 and must not be default
        if len(self._caption) < Numbers.article_image_caption_min or len(
                self._caption) > Numbers.article_image_caption_max:
            self._caption_error_message = Strings.seo_error_image_caption_length
            result = False

        if self._caption == Strings.label_article_image_caption:
            self._caption_error_message = Strings.seo_error_default_value
            result = False

        # Check thumbnail image disk path
        if not self._thumbnail_path or not os.path.exists(self._thumbnail_path):
            # The image has the same dimensions as the main image
            self._image = wx.Image(Fetch.get_resource_path('main_image_thumbnail_missing.png'), wx.BITMAP_TYPE_PNG)
            self._thumbnail_size = self._image.GetSize()
            result = False
        else:
            image = wx.Image(Fetch.get_resource_path(self._thumbnail_path), wx.BITMAP_TYPE_ANY)
            self._thumbnail_size = image.GetSize()
            if self._thumbnail_size == (Numbers.main_image_width, Numbers.main_image_height):
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

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_caption(self) -> (str, str):
        """
        Return the image caption and error to display in gui if there is one.
        :return: Return the article name as it is in the menu item and error to display in gui if there is one.
        """
        return self._caption, self._caption_error_message

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_caption(self, caption: str) -> None:
        """
        Set new image caption
        :param caption: The new caption
        :return: None
        """
        if self._caption != caption:
            self._caption = caption
            self._modified = True

    def __str__(self) -> str:
        return "Aside image: {}, original: {}, thumbnail: {}, title: {}, alt: {}".format(self._caption,
                                                                                         self._original_image_path,
                                                                                         self._thumbnail_path,
                                                                                         self._link_title,
                                                                                         self._image_alt)
