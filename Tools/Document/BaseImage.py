import os

import wx

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Resources.Fetch import Fetch
from Tools.SpellCheckedObject import SpellCheckedObject


class BaseImage(SpellCheckedObject):
    """
    Base class for AsideImage and ImageInText.
    """

    count: int = 1

    def __init__(self, title: str, image_alt: str, original_image_path: str, thumbnail_path: str, full_filename: str,
                 thumbnail_filename: str):
        """
        Constructor for a base image instance.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param original_image_path: full disk path to the original size image.
        :param thumbnail_path: full path to the thumbnail image.
        :param full_filename: file name of the full image
        :param thumbnail_filename: file name of the thumbnail image
        """
        super().__init__()
        self._link_title = title
        self._link_title_error_message: str = ''
        self._image_alt = image_alt
        self._image_alt_error_message: str = ''
        self._original_image_path = original_image_path
        self._thumbnail_path = thumbnail_path
        self._full_filename = full_filename
        self._thumbnail_filename = thumbnail_filename
        self._image = None
        self._status_color = None
        self._thumbnail_size = (0, 0)
        self._original_size = (0, 0)
        self._modified = False

        # Create a unique ID.
        self._image_id = str(BaseImage.count)
        BaseImage.count += 1

    def test_self(self) -> bool:
        """
        SEO test self for alt and link title. If the image and thumbnail is not accessible on disk, set a special
        warning image.
        :return: True if test is ok, False otherwise
        """
        # Disk paths have to be checked by the subclasses.
        # Clear all error before each retest
        self._link_title_error_message = ''
        self._image_alt_error_message = ''
        self._status_color = wx.NullColour

        result = True
        # Check article image link title
        if len(self._link_title) < Numbers.article_image_title_min or len(
                self._link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            result = False

        if self._link_title == Strings.label_article_image_link_title:
            self._link_title_error_message = Strings.seo_error_default_value
            result = False

        # Check article image alt
        if len(self._image_alt) < Numbers.article_image_alt_min or len(
                self._image_alt) > Numbers.article_image_alt_max:
            self._image_alt_error_message = Strings.seo_error_image_alt_length
            result = False

        if self._image_alt == Strings.label_article_image_alt:
            self._image_alt_error_message = Strings.seo_error_default_value
            result = False

        # Spell checks
        if not self._spell_check(self._link_title):
            self._link_title_error_message = Strings.spelling_error
            result = False

        if not self._spell_check(self._image_alt):
            self._image_alt_error_message = Strings.spelling_error
            result = False

        if not result:
            self._status_color = wx.RED
        return result

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_id(self) -> str:
        """
        Return the ID of this image.
        :return: Return the ID of this image.
        """
        return self._image_id

    def is_modified(self) -> bool:
        """
        Return true if this instance was modified.
        :return: Return true if this instance was modified.
        """
        return self._modified

    def get_link_title(self) -> (str, str):
        """
        Return the link title of the image and error to display in gui if there is one.
        :return: Return the link title of the image item and error to display in gui if there is one.
        """
        return self._link_title, self._link_title_error_message

    def get_image_alt(self) -> (str, str):
        """
        Return the image alt description and error to display in gui if there is one.
        :return: Return the image alt description and error to display in gui if there is one.
        """
        return self._image_alt, self._image_alt_error_message

    def get_original_image_path(self) -> str:
        """
        Return the original image full disk path.
        :return: Return the original image full disk path, None if inaccessible.
        """
        return self._original_image_path

    def get_thumbnail_image_path(self) -> str:
        """
        Return the thumbnail image full disk path.
        :return: Return the thumbnail image full disk path, None if inaccessible.
        """
        return self._thumbnail_path

    def get_thumbnail_filename(self) -> str:
        """
        Return the thumbnail image file name.
        :return: Return the thumbnail image filename.
        """
        return self._thumbnail_filename

    def get_full_filename(self) -> str:
        """
        Return the full image file name.
        :return: Return the full image filename.
        """
        return self._full_filename

    def get_image(self, normal: bool = False) -> wx.Image:
        """
        Return the image as wx image instance. If there was a seo error the image will be red.
        :param normal: Do not return red image even if there was a problem.
        :return: Return the image as wx image instance.
        """
        if normal:
            return self._image
        if self._status_color == wx.RED:
            return self._image.AdjustChannels(0.9, 0.5, 0.5)
        return self._image

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this image. White if ok, Red if SEO check failed.
        :return: Return the status color of this image. White if ok, Red if SEO check failed.
        """
        return self._status_color

    def get_thumbnail_size(self) -> (int, int):
        """
        Return a tuple of this image's thumbnail size (width, height).
        :return: Return a tuple of this image's thumbnail size (width, height).
        """
        return self._thumbnail_size

    def get_original_size(self) -> (int, int):
        """
        Return a tuple of this image's original size (width, height).
        :return: Return a tuple of this image's original size (width, height).
        """
        if not self._original_image_path:
            return None
        if not os.path.exists(self._original_image_path):
            return None
        image = wx.Image(Fetch.get_resource_path(self._original_image_path), wx.BITMAP_TYPE_ANY)
        self._original_size = image.GetSize()
        return self._original_size

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_link_title(self, title: str) -> None:
        """
        Set new title
        :param title: The new title
        :return: None
        """
        if self._link_title != title:
            self._link_title = title
            self._modified = True

    def set_alt(self, alt: str) -> None:
        """
        Set new alt description
        :param alt: The new alt description
        :return: None
        """
        if self._image_alt != alt:
            self._image_alt = alt
            self._modified = True

    def set_original_image_path(self, path: str) -> None:
        """
        Set new original image path.
        :param path: The new original image path.
        :return: None
        """
        if self._original_image_path != path:
            self._original_image_path = path
            self._modified = True

    def set_thumbnail_image_path(self, path: str) -> None:
        """
        Set new thumbnail image path.
        :param path: The new thumbnail image path.
        :return: None
        """
        if self._thumbnail_path != path:
            self._thumbnail_path = path
            self._modified = True

    def set_full_filename(self, name: str) -> None:
        """
        Set new original image filename.
        :param name: The new original image filename.
        :return: None
        """
        if self._full_filename != name:
            self._full_filename = name
            self._modified = True

    def set_thumbnail_filename(self, name: str) -> None:
        """
        Set new thumbnail image filename.
        :param name: The new thumbnail image filename.
        :return: None
        """
        if self._thumbnail_filename != name:
            self._thumbnail_filename = name
            self._modified = True

    def set_modified(self, modified: bool) -> None:
        """
        Set new modified state.
        :param modified: True or False
        :return: None
        """
        self._modified = modified

    def __str__(self) -> str:
        return "Base image: id {}, original: {}, thumbnail: {}, title: {}, alt: {}".format(self._image_id,
                                                                                           self._original_image_path,
                                                                                           self._thumbnail_path,
                                                                                           self._link_title,
                                                                                           self._image_alt)
