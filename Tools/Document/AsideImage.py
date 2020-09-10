import wx

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Resources.Fetch import Fetch


class AsideImage:
    """
    Carrier class for a parsed aside image.
    """

    def __init__(self, caption: str, title: str, image_alt: str,
                 original_image_path: str, thumbnail_path: str):
        """
        Constructor for an aside image.
        :param caption: Figcaption of the aside image.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param original_image_path: full disk path to the original size image.
        :param thumbnail_path: full path to the thumbnail image.
        """
        self._caption = caption
        self._caption_error_message: str = ''
        self._link_title = title
        self._link_title_error_message: str = ''
        self._image_alt = image_alt
        self._image_alt_error_message: str = ''
        self._original_image_path = original_image_path
        self._thumbnail_path = thumbnail_path
        self._image = None

    def seo_test_self(self) -> bool:
        """
        SEO test self for caption, alt and link title. If the image and thumbnail is not accessible on disk, set a
        special warning image.
        :return: True if test is ok, False otherwise
        """
        # Clear all error before each retest
        self._caption_error_message: str = ''
        self._link_title_error_message: str = ''
        self._image_alt_error_message: str = ''

        result = True
        # Check caption length must be at least 3 and must not be default
        if len(self._caption) < Numbers.article_name_min_length or len(
                self._caption) > Numbers.article_name_max_length:
            self._caption_error_message = Strings.seo_error_name_length
            result = False

        if self._caption == Strings.label_article_image_caption:
            self._caption_error_message = Strings.seo_error_default_value
            result = False

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

        # Check thumbnail image disk path
        if not self._thumbnail_path:
            self._image = wx.Image(Fetch.get_resource_path('aside_image_thumbnail_missing.png'), wx.BITMAP_TYPE_PNG)
            result = False
        else:
            image = wx.Image(Fetch.get_resource_path(self._thumbnail_path), wx.BITMAP_TYPE_ANY)
            if image.GetSize() == (Numbers.main_image_width, Numbers.main_image_height):
                self._image = image
            else:
                self._image = wx.Image(Fetch.get_resource_path('aside_image_thumbnail_wrong.png'), wx.BITMAP_TYPE_PNG)
                result = False

            # Check full image disk path, size can be whatever the user likes
            if not self._original_image_path:
                self._image = wx.Image(Fetch.get_resource_path('aside_image_missing.png'), wx.BITMAP_TYPE_PNG)
                result = False

        return result

    def get_image_caption(self) -> (str, str):
        """
        Return the image caption and error to display in gui if there is one.
        :return: Return the article name as it is in the menu item and error to display in gui if there is one.
        """
        return self._caption, self._caption_error_message

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
        return self._original_image_path

    def get_image(self) -> wx.Image:
        """
        Return the image as wx image instance.
        :return: Return the image as wx image instance.
        """
        return self._image

    def __str__(self) -> str:
        return "Aside image: {}, original: {}, thumbnail: {}, title: {}, alt: {}".format(self._caption,
                                                                                         self._original_image_path,
                                                                                         self._thumbnail_path,
                                                                                         self._link_title,
                                                                                         self._image_alt)
