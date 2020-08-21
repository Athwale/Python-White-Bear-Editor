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
        self._link_title = title
        self._image_alt = image_alt
        self._href = href
        self._menu_image_path = disk_path

    def get_menu_article_name(self) -> str:
        """
        Return the article name as it is in the menu item. May be different from the title on the actual article page.
        :return: Return the article name as it is in the menu item.
        """
        return self._article_name

    def get_menu_link_title(self) -> str:
        """
        Return the link title of the menu item.
        :return: Return the link title of the menu item.
        """
        return self._link_title

    def get_menu_image_alt(self) -> str:
        """
        Return the image alt description of the menu item.
        :return: Return the image alt description of the menu item.

        """
        return self._image_alt

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
