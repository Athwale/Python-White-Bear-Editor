import wx

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Resources.Fetch import Fetch
from Tools.SpellCheckedObject import SpellCheckedObject


class MenuItem(SpellCheckedObject):
    """
    Carrier class for a parsed menu item.
    """

    def __init__(self, name: str, title: str, image_alt: str, href: str, disk_path: str, img_filename: str):
        """
        Constructor for a menu item.
        :param name: Name of the article in the menu.
        :param title: html title of the link element.
        :param image_alt: html alt description of the img element.
        :param href: link to the article html page.
        :param disk_path: path to the menu image.
        :param img_filename: The filename of the menu image
        """
        super().__init__()
        self._article_name = name
        self._article_name_error_message: str = ''
        self._link_title = title
        self._link_title_error_message: str = ''
        self._image_alt = image_alt
        self._image_alt_error_message: str = ''
        self._href = href
        self._menu_image_path = disk_path
        self._menu_image = None
        self._modified = False
        self._status_color = None
        self._filename = img_filename
        self._article = None

    def copy(self):
        """
        Returns a copy of this menu item.
        :return: A copy of this menu item.
        """
        return MenuItem(self.get_article_name()[0], self.get_link_title()[0], self.get_image_alt()[0],
                        self.get_link_href(), self.get_image_path(), self.get_filename())

    def test_self(self) -> bool:
        """
        SEO test self for page name, alt and link title. If the menu image is not accessible on disk, set a special
        warning image.
        :return: True if test is ok, False otherwise
        """
        # Clear all error before each retest
        self._article_name_error_message: str = ''
        self._link_title_error_message: str = ''
        self._image_alt_error_message: str = ''
        self._status_color = wx.NullColour

        result = True
        # Check page name length must be at least 3 and must not be default
        if len(self._article_name) < Numbers.menu_name_min_length or len(
                self._article_name) > Numbers.menu_name_max_length:
            self._article_name_error_message = Strings.seo_error_menu_name_length
            result = False

        if self._article_name == Strings.label_article_menu_logo_name_placeholder:
            self._article_name_error_message = Strings.seo_error_default_value
            result = False

        # Check menu image disk path
        if not self._menu_image_path:
            self._menu_image = wx.Image(Fetch.get_resource_path('menu_image_missing.png'), wx.BITMAP_TYPE_PNG)
            result = False
        else:
            try:
                image = wx.Image(Fetch.get_resource_path(self._menu_image_path), wx.BITMAP_TYPE_ANY)
                if image.GetSize() == (Numbers.menu_logo_image_size, Numbers.menu_logo_image_size):
                    self._menu_image = image
                else:
                    self._menu_image = wx.Image(Fetch.get_resource_path('menu_image_wrong.png'), wx.BITMAP_TYPE_PNG)
                    result = False
            except FileNotFoundError as _:
                self._menu_image = wx.Image(Fetch.get_resource_path('menu_image_missing.png'), wx.BITMAP_TYPE_PNG)
                result = False

        # Check article image link title
        if len(self._link_title) < Numbers.article_image_title_min or len(
                self._link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            result = False

        if self._link_title == Strings.label_menu_logo_link_title_placeholder:
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

        # Spellchecks
        if not self._spell_check(self._article_name):
            self._article_name_error_message = Strings.spelling_error
            result = False

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
    def get_article_name(self) -> (str, str):
        """
        Return the article name as it is in the menu item. May be different from the title on the actual article page
        and error to display in gui if there is one.
        :return: Return the article name as it is in the menu item and error to display in gui if there is one.
        """
        return self._article_name, self._article_name_error_message

    def get_link_title(self) -> (str, str):
        """
        Return the link title of the menu item and error to display in gui if there is one.
        :return: Return the link title of the menu item and error to display in gui if there is one.
        """
        return self._link_title, self._link_title_error_message

    def get_image_alt(self) -> (str, str):
        """
        Return the image alt description of the menu item and error to display in gui if there is one.
        :return: Return the image alt description of the menu item and error to display in gui if there is one.
        """
        return self._image_alt, self._image_alt_error_message

    def get_link_href(self) -> str:
        """
        Return the link href of the menu item.
        :return: Return the link href of the menu item.
        """
        return self._href

    def get_image_path(self) -> str:
        """
        Return the image disk path of the menu item.
        :return: Return the image disk path of the menu item. None if the file is inaccessible on hard drive.
        """
        return self._menu_image_path

    def get_image(self, normal: bool = False) -> wx.Image:
        """
        Return the image as wx image instance. If there was a seo error the image will be red.
        :param normal: Do not return red image even if there was a problem.
        :return: Return the image as wx image instance.
        """
        if normal:
            return self._menu_image
        if self._status_color == wx.RED:
            return self._menu_image.AdjustChannels(0.9, 0.5, 0.5)
        return self._menu_image

    def get_image_size(self) -> (int, int):
        """
        Return the menu image size (width, height).
        :return: Return the menu image size (width, height).
        """
        return self._menu_image.GetSize()

    def get_filename(self) -> str:
        """
        Return the image file name.
        :return: Return the image filename.
        """
        return self._filename

    def get_article(self):
        """
        Return the document this item belongs to.
        :return: The document this item belongs to.
        """
        return self._article

    def is_modified(self) -> bool:
        """
        Return true if this instance was modified.
        :return: Return true if this instance was modified.
        """
        return self._modified

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_article(self, article) -> None:
        """
        Set a which article this item belongs to.
        :param article: The article
        :return: None
        """
        if self._article != article:
            self._article = article
            self._modified = True

    def set_article_name(self, new_name: str) -> None:
        """
        Set a new name for this menu item. The name is displayed under the image.
        :param new_name: The new name.
        :return: None
        """
        if self._article_name != new_name:
            self._article_name = new_name
            self._modified = True

    def set_link_title(self, new_title: str) -> None:
        """
        Set a new link title for this menu item.
        :param new_title: The new title.
        :return: None
        """
        if self._link_title != new_title:
            self._link_title = new_title
            self._modified = True

    def set_image_alt(self, new_alt: str) -> None:
        """
        Set a new image alt description for this menu item.
        :param new_alt: The new image alt description.
        :return: None
        """
        if self._image_alt != new_alt:
            self._image_alt = new_alt
            self._modified = True

    def set_href(self, new_href: str) -> None:
        """
        Set a new link href for this menu item.
        :param new_href: The new link href.
        :return: None
        """
        if self._href != new_href:
            self._href = new_href
            self._modified = True

    def set_image_path(self, new_path: str) -> None:
        """
        Set a new image disk path for this menu item.
        :param new_path: The new image disk path.
        :return: None
        """
        if self._menu_image_path != new_path:
            self._menu_image_path = new_path
            self._modified = True

    def set_filename(self, filename: str) -> None:
        """
        Set a new filename for this menu item.
        :param filename: The new filename.
        :return: None
        """
        if self._filename != filename:
            self._filename = filename
            self._modified = True

    def set_modified(self, modified: bool) -> None:
        """
        Set new modified state.
        :param modified: True or False
        :return: None
        """
        self._modified = modified

    def __str__(self) -> str:
        return "Menu item {}, Link {}, Image {}".format(self._article_name, self._href, self._menu_image_path)
