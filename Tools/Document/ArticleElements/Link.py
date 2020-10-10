import os

import requests
import wx

from Constants.Constants import Numbers, Strings


class Link:
    """
    Represents a link inside text.
    """

    def __init__(self, text: str, url: str, title: str, loaded_pages, working_directory: str):
        """
        Constructor for a Link.
        :param text: The visible text of the link.
        :param url: The URL of the link.
        :param title: The html title of the link.
        :param loaded_pages: A dictionary of all other loaded pages.
        :param working_directory: The working directory of the editor.
        """
        # All link target blank page except links in menus which we do not parse here.
        self._text = text
        self._text_error_message = ''
        self._url = url
        self._url_error_message: str = ''
        self._link_title = title
        self._link_title_error_message: str = ''
        self._working_directory = working_directory

        self._loaded_pages = loaded_pages
        self._is_local = False
        self._status_color = None

    def seo_test_self(self):
        """
        SEO check self for correct title, url and text.
        :return: True if no error is found.
        """
        # Disk paths have to be checked by the sub classes.
        # Clear all error before each retest
        self._link_title_error_message = ''
        self._url_error_message = ''
        self._text_error_message = ''
        self._status_color = wx.NullColour

        result = True
        # Check link title
        if len(self._link_title) < Numbers.article_image_title_min or len(
                self._link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            result = False

        # Check link text
        if len(self._text) < Numbers.article_name_min_length or len(
                self._link_title) > Numbers.article_name_max_length:
            self._link_title_error_message = Strings.seo_error_link_title_length
            result = False

        # Check url, if it is one of whitebear pages set local to True and do not try to download it.
        if self._url in list(self._loaded_pages.keys()):
            self._is_local = True
        elif self._url.startswith('files'):
            full_path = os.path.join(self._working_directory, self._url)
            if not os.path.exists(full_path) or not os.access(full_path, os.R_OK) or not os.access(full_path, os.W_OK):
                result = False
        else:
            self._is_local = False
            try:
                requests.get(self._url)
            except requests.ConnectionError as _:
                self._url_error_message = Strings.seo_error_url_nonexistent
                result = False

        if not result:
            self._status_color = wx.RED
        return result

    def get_text(self) -> str:
        """
        Return the visible text of the link.
        :return: the visible text of the link.
        """
        return self._text

    def get_url(self) -> str:
        """
        Return the url of the link.
        :return: the url of the link.
        """
        return self._url

    def get_title(self) -> str:
        """
        Return the title of the link.
        :return: the title of the link.
        """
        return self._link_title

    def is_local(self) -> bool:
        """
        Returns True if this link aims back at one of the whitebear pages.
        :return: Returns True if this link aims back at one of the whitebear pages.
        """
        return self._is_local

    def set_text(self, text: str) -> None:
        """
        Set a new visible text for the link.
        :param text: The new text to display.
        :return: None
        """
        self._text = text

    def set_url(self, url: str) -> None:
        """
        Set a new url for the link.
        :param url: The new url.
        :return: None
        """
        self._url = url

    def set_title(self, title: str) -> None:
        """
        Set a new title for the link.
        :param title: The new title.
        :return: None
        """
        self._link_title = title

    def set_local(self, is_local: bool) -> None:
        """
        Set whether this link aims back to one of the whitebear web pages.
        :param is_local: True if yes.
        :return: None
        """
        self._is_local = is_local
