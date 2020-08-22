import os
from typing import List, Dict

import wx
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Strings import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Exceptions.WrongFormatException import WrongFormatException
from Resources.Fetch import Fetch
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu


class WhitebearDocumentArticle(WhitebearDocument):
    """
    This class represents an article file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str, menus: Dict[str, WhitebearDocumentMenu]):
        """
        Create a new WhitebearDocumentArticle object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        :param menus: A list of WhitebearDocuments representing menus
        """
        # File properties are in base class
        super().__init__(name, path, menus)

        # Article data
        self._status_color = wx.RED
        self._menu_section = None
        self._menu_item = None
        self._date = None
        self._article_full_image_path = None
        self._article_thumbnail_image_path = None
        self._article_image_caption = ''
        self._article_image_link_title = None
        self._article_image_alt = None
        self._article_image = None
        # Menu item data
        self._menu_image_path = None
        self._menu_item_name = None
        self._menu_image_alt = None
        self._menu_image_link_title = None
        self._menu_image = None

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Only parse if not parsed already and only if the document is valid.
        # TODO create the wx image instances after seo check passed and the images have correct size
        if not self._parsed_html and self.is_valid():
            super(WhitebearDocumentArticle, self).parse_self()
            self._parse_page_name()
            self._parse_article_image_path()
            self._parse_article_image_caption()
            self._parse_article_image_link_title()
            self._parse_article_image_alt()
            self._determine_menu_section_and_menu_item()

    def _determine_menu_section_and_menu_item(self):
        """
        Find out which menu this article belongs in.
        :return: None
        :raises WrongFormatException: If the article is not found in any menu.
        """
        for menu in self._menus.values():
            self._menu_item = menu.find_item_by_file_name(self.get_filename())
            if self._menu_item:
                self._menu_section = menu.get_page_name()
                break
        if not self._menu_item:
            raise WrongFormatException(Strings.exception_menu_item_missing + ' for: ' + self.get_filename())

    def _parse_page_name(self):
        """
        Parse the name of this article and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'textPage'})
        self._page_name = article.h2.string

    def _parse_date(self):
        """
        Parse the date stamp of this document and save it into an instance variable.
        :return: None
        """
        self._date = self._parsed_html.find(name='p', attrs={'id': 'date'}).string

    def _parse_article_image_path(self):
        """
        Parse the absolute path to the main article image and save it into an instance variable.
        If the image is not accessible on disk, the variable is set to None.
        :return: None
        """
        main_image_figure = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'})
        self._article_full_image_path = os.path.join(self._working_directory, main_image_figure.a['href'])
        self._article_thumbnail_image_path = os.path.join(self._working_directory, main_image_figure.img['src'])
        if not os.path.exists(self._article_full_image_path) or \
                not os.access(self._article_full_image_path, os.R_OK) or \
                not os.access(self._article_full_image_path, os.W_OK):
            self._article_full_image_path = None

        if not os.path.exists(self._article_thumbnail_image_path) or \
                not os.access(self._article_thumbnail_image_path, os.R_OK) or \
                not os.access(self._article_thumbnail_image_path, os.W_OK):
            self._article_thumbnail_image_path = None

    def _parse_article_image_caption(self):
        """
        Parse the main article image caption text and save it into an instance variable.
        :return: None
        """
        main_image_figure = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'})
        # The figcaption tag is allowed to contain <br> which we have to skip
        string_content = main_image_figure.figcaption.strings
        self._article_image_caption = ''.join(string_content)

    def _parse_article_image_link_title(self):
        """
        Parse the main article image link title text and save it into an instance variable.
        :return: None
        """
        self._article_image_link_title = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'}).a['title']

    def _parse_article_image_alt(self):
        """
        Parse the main article image alt description text and save it into an instance variable.
        :return: None
        """
        self._article_image_alt = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'}).img['alt']

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the article xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        errors = []
        try:
            xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_article.xsd')))
            xml_doc = html.parse(self.get_path())
            self._valid = xmlschema.validate(xml_doc)
        except XMLSyntaxError as e:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + str(e))
        for error in xmlschema.error_log:
            errors.append(error.message)
        return self._valid, errors

    def seo_test_self(self):
        """

        :return:
        """
        # TODO seo test should return what to display in the gui about text lengths etc and document completeness.
        # TODO the file list can change color based on the result of this method. Files have to be valid before this
        # TODO test. Do a second pass over all loaded and now valid documents and color the list based on this method.
        # TODO save the filelist color in this instance, run self test on every setter method.
        pass

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_date(self) -> str:
        """
        Return the article creation date.
        :return: Return article creation date.
        """
        return self._date

    def get_article_image_path(self) -> str:
        """
        Return the path to the article image full version.
        :return: Return the path to the article image full version.
        """
        return self._article_full_image_path

    def get_article_image(self) -> wx.Image:
        """
        Return the article image wx image instance.
        :return: Return the article image wx image instance.
        """
        return self._article_image

    def get_article_image_caption(self) -> str:
        """
        Return the caption of the main article image.
        :return: Return the caption of the main article image.
        """
        return self._article_image_caption

    def get_article_image_link_title(self) -> str:
        """
        Return the link title of the main article image.
        :return: Return the link title of the main article image.
        """
        return self._article_image_link_title

    def get_article_image_alt(self) -> str:
        """
        Return the alt description of the main article image.
        :return: Return the alt description of the main article image.
        """
        return self._article_image_alt

    def get_menu_image(self) -> wx.Image:
        """
        Return the menu image wx image instance.
        :return: Return the menu image wx image instance.
        """
        return self._menu_image

    def get_menu_item(self) -> MenuItem:
        """
        Return the menu item associated with this article.
        :return: The menu item associated with this article.
        """
        return self._menu_item

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        :return: Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        """
        return self._status_color

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_date(self, date: str) -> None:
        """
        Set the new article date.
        Change modified attribute to True.
        :param date: New article creation date.
        :return: None
        """
        self._date = date
        self.set_modified(True)

    def set_article_image_path(self, path: str) -> None:
        """
        Set the new main article image file path for the full version.
        Change modified attribute to True.
        :param path: New image path in disk.
        :return: None
        """
        self._article_full_image_path = path
        self.set_modified(True)

    def set_article_image_caption(self, text: str) -> None:
        """
        Set the new main article image caption.
        Change modified attribute to True.
        :param text: New image caption.
        :return: None
        """
        self._article_image_caption = text
        self.set_modified(True)

    def set_article_image_link_title(self, text: str) -> None:
        """
        Set the new main article image link title.
        Change modified attribute to True.
        :param text: New image link title.
        :return: None
        """
        self._article_image_link_title = text
        self.set_modified(True)

    def set_article_image_alt(self, text: str) -> None:
        """
        Set the new main article image alt description.
        Change modified attribute to True.
        :param text: New image alt description.
        :return: None
        """
        self._article_image_alt = text
        self.set_modified(True)

    def set_status_color(self, new_color: wx.Colour) -> None:
        """
        Set new status color.
        :param new_color: New wx.Colour color.
        :return: None
        """
        self._status_color = new_color
        self.set_modified(True)