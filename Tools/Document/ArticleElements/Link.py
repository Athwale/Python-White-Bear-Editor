import os
from ssl import SSLCertVerificationError
from typing import List

import httplib2
import wx

from Constants.Constants import Numbers, Strings


class Link:
    """
    Represents a link inside text.
    """

    count: int = 1

    def __init__(self, text: str, url: str, title: str, loaded_pages, working_directory: str):
        """
        Constructor for a Link, creates a new link with a unique ID.
        :param text: The visible text of the link.
        :param url: The URL of the link.
        :param title: The html title of the link.
        :param loaded_pages: A dictionary of all other loaded pages.
        :param working_directory: The working directory of the editor.
        """
        # All link target blank page except links in menus which we do not parse here.
        self._link_id: str = ''
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
        self._modified = False

        # Create a unique ID.
        self._link_id = str(Link.count)
        Link.count = Link.count + 1

    def seo_test_self(self, online: bool):
        """
        SEO check self for correct title, url and text.
        :param online: Do online url test.
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
            self._text_error_message = Strings.seo_error_name_length
            result = False

        # Check url, if it is one of whitebear pages set local to True and do not try to download it.
        if self._url in list(self._loaded_pages.keys()):
            self._is_local = True
        elif self._url.startswith(Strings.folder_files):
            full_path = os.path.join(self._working_directory, self._url)
            if not os.path.exists(full_path) or not os.access(full_path, os.R_OK) or not os.access(full_path, os.W_OK):
                self._url_error_message = Strings.seo_error_url_nonexistent
                result = False
        else:
            self._is_local = False
            if online:
                h = httplib2.Http(timeout=Numbers.online_test_timeout)
                try:
                    resp = h.request(self._url, 'HEAD')
                    if int(resp[0]['status']) >= 400:
                        self._url_error_message = Strings.seo_error_url_nonexistent
                        result = False
                except KeyError as _:
                    self._url_error_message = Strings.seo_error_url_malformed
                    result = False
                except (httplib2.ServerNotFoundError, httplib2.RelativeURIError, SSLCertVerificationError) as _:
                    self._url_error_message = Strings.seo_error_url_nonexistent
                    result = False
                except ConnectionResetError as _:
                    pass
                finally:
                    h.close()

        if not result:
            self._status_color = wx.RED
        return result

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_id(self) -> str:
        """
        Return the ID of this link.
        :return: Return the ID of this link.
        """
        return self._link_id

    def get_text(self) -> (str, str):
        """
        Return the visible text of the link and any text error.
        :return: the visible text of the link and any text error.
        """
        return self._text, self._text_error_message

    def get_url(self) -> (str, str):
        """
        Return the url of the link and any error.
        :return: the url of the link and any error.
        """
        return self._url, self._url_error_message

    def get_title(self) -> (str, str):
        """
        Return the title of the link and any error.
        :return: the title of the link and any error.
        """
        return self._link_title, self._link_title_error_message

    def get_loaded_pages(self) -> List[str]:
        """
        Return a list of all other loaded whitebear page names.
        :return: a list of all other loaded whitebear page names.
        """
        return list(self._loaded_pages.keys())

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this link. RED if SEO failed.
        :return: Return the status color of this link. RED if SEO failed.
        """
        return self._status_color

    def is_local(self) -> bool:
        """
        Returns True if this link aims back at one of the whitebear pages.
        :return: Returns True if this link aims back at one of the whitebear pages.
        """
        return self._is_local

    def is_modified(self) -> bool:
        """
        Return true if this instance was modified.
        :return: Return true if this instance was modified.
        """
        return self._modified

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_text(self, text: str) -> None:
        """
        Set a new visible text for the link.
        :param text: The new text to display.
        :return: None
        """
        if self._text != text:
            self._text = text
            self._modified = True

    def set_url(self, url: str) -> None:
        """
        Set a new url for the link.
        :param url: The new url.
        :return: None
        """
        if self._url != url:
            self._url = url
            self._modified = True

    def set_title(self, title: str) -> None:
        """
        Set a new title for the link.
        :param title: The new title.
        :return: None
        """
        if self._link_title != title:
            self._link_title = title
            self._modified = True

    def set_local(self, is_local: bool) -> None:
        """
        Set whether this link aims back to one of the whitebear web pages.
        :param is_local: True if yes.
        :return: None
        """
        if self._is_local != is_local:
            self._is_local = is_local
            self._modified = True

    def set_modified(self, modified: bool) -> None:
        """
        Set new modified state.
        :param modified: True or False
        :return: None
        """
        self._modified = modified

    def __str__(self) -> str:
        return 'Link: id: ' + str(self._link_id) + ', text: ' + self._text + ', url: ' + self._url + ', title: ' + \
               self._link_title
