import wx

from Constants.Numbers import Numbers
from Constants.Strings import Strings
from Resources.Fetch import Fetch


class MenuItem:
    """
    Carrier class for a parsed menu item.
    """

    def __init__(self, name: str, title: str, image_alt: str, href: str, disk_path: str):
        """
        Constructor for a menu item.
        :param name: Name of the article in the menu.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param href: link to the article html page.
        :param disk_path: path to the menu image.
        """
        self._article_name = name
        self._article_name_error_message: str = ''
        self._link_title = title
        self._link_title_error_message: str = ''
        self._image_alt = image_alt
        self._image_alt_error_message: str = ''
        self._href = href
        self._menu_image_path = disk_path
        self._menu_image = None

    def seo_test_self(self) -> bool:
        """
        SEO test self for page name, alt and link title. If the menu image is not accessible on disk, set a special
        warning image.
        :return: True if test is ok, False otherwise
        """
        # Clear all error before each retest
        self._article_name_error_message: str = ''
        self._link_title_error_message: str = ''
        self._image_alt_error_message: str = ''

        result = True
        # Check page name length must be at least 3 and must not be default
        if len(self._article_name) < Numbers.article_name_min_length or len(
                self._article_name) > Numbers.article_name_max_length:
            self._article_name_error_message = Strings.seo_error_name_length
            result = False

        if self._article_name == Strings.label_article_menu_logo_name_placeholder:
            self._article_name_error_message = Strings.seo_error_default_value
            result = False

        # Check menu image disk path
        if not self._menu_image_path:
            self._menu_image = wx.Image(Fetch.get_resource_path('menu_image_missing.png'), wx.BITMAP_TYPE_PNG)
            result = False
        else:
            image = wx.Image(Fetch.get_resource_path(self._menu_image_path), wx.BITMAP_TYPE_ANY)
            if image.GetSize() == (Numbers.logo_image_size, Numbers.logo_image_size):
                self._menu_image = image
            else:
                self._menu_image = wx.Image(Fetch.get_resource_path('menu_image_wrong.png'), wx.BITMAP_TYPE_ANY)
                result = False

        # Check article image link title
        if len(self._link_title) < Numbers.article_image_title_min or len(
                self._link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            result = False

        if self._link_title == Strings.label_article_menu_logo_link_title_placeholder:
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

        return result

    def get_menu_article_name(self) -> (str, str):
        """
        Return the article name as it is in the menu item. May be different from the title on the actual article page
        and error to display in gui if there is one.
        :return: Return the article name as it is in the menu item and error to display in gui if there is one.
        """
        return self._article_name, self._article_name_error_message

    def get_menu_link_title(self) -> (str, str):
        """
        Return the link title of the menu item and error to display in gui if there is one.
        :return: Return the link title of the menu item and error to display in gui if there is one.
        """
        return self._link_title, self._link_title_error_message

    def get_menu_image_alt(self) -> (str, str):
        """
        Return the image alt description of the menu item and error to display in gui if there is one.
        :return: Return the image alt description of the menu item and error to display in gui if there is one.
        """
        return self._image_alt, self._image_alt_error_message

    def get_menu_link_href(self) -> str:
        """
        Return the link href of the menu item.
        :return: Return the link href of the menu item.
        """
        return self._href

    def get_menu_image_path(self) -> str:
        """
        Return the image disk path of the menu item.
        :return: Return the image disk path of the menu item. None if the file is inaccessible on hard drive.
        """
        return self._menu_image_path

    def get_menu_image(self) -> wx.Image:
        """
        Return the menu image wx image instance.
        :return: Return the menu image wx image instance.
        """
        return self._menu_image

    def __str__(self) -> str:
        return "Menu item {}, Link {}, Image {}".format(self._article_name, self._href, self._menu_image_path)
