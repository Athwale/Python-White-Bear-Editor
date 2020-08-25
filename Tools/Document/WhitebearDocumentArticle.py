import os
import re
from typing import List, Dict

import wx
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Numbers import Numbers
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
        self._date_regex = '^[1-9][0-9]{0,1}[.][ ](' + Strings.cz_months + ')[ ][1-9][0-9][0-9][0-9]$'

        # Article data
        self._menu_section = None
        self._menu_item = None

        self._date = None
        self._date_error_message: str = ''
        self._article_full_image_path = None
        self._article_thumbnail_image_path = None
        self._article_image_caption = ''
        self._caption_error_message: str = ''
        self._article_image_link_title = None
        self._link_title_error_message: str = ''
        self._article_image_alt = None
        self._image_alt_error_message: str = ''
        self._article_image = None

        # TODO parse and validate main text
        self._main_text = None
        # TODO parse and validate aside images. Store them in a separate carrier class and implement a panel subclass
        # TODO for the gui to display with rearrangement possible.

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Only parse if not parsed already.
        # TODO create the wx image instances after seo check passed and the images have correct size
        if not self._parsed_html:
            super(WhitebearDocumentArticle, self).parse_self()
            self._parse_page_name()
            self._parse_date()
            self._parse_article_image_path()
            self._parse_article_image_caption()
            self._parse_article_image_link_title()
            self._parse_article_image_alt()
            self._determine_menu_section_and_menu_item()
            self.seo_test_self()

    def seo_test_self(self):
        """

        :return:
        """
        # TODO Run self test on every setter method.
        # Check meta keywords and description
        super(WhitebearDocumentArticle, self).seo_test_self_basic()
        # Check page name length must be at least 3 and must not be default
        if len(self._page_name) < Numbers.article_name_min_length or len(
                self._page_name) > Numbers.article_name_max_length:
            self._page_name_error_message = Strings.seo_error_name_length
            self.set_status_color(wx.RED)

        if self._page_name == Strings.label_article_title:
            self._page_name_error_message = Strings.seo_error_default_value
            self.set_status_color(wx.RED)

        # Check date format
        if not re.search(self._date_regex, self._date):
            self._date_error_message = Strings.seo_error_date_format
            self.set_status_color(wx.RED)
        else:
            day, _, year = self._date.split(' ', 3)
            # Check day range
            if int(day.replace('.', '')) < 1 or int(day.replace('.', '')) > 31:
                self._date_error_message = Strings.seo_error_date_format_day
                self.set_status_color(wx.RED)

            # Check year range
            if int(year) < Numbers.year_min or int(year) > Numbers.year_max:
                self._date_error_message = Strings.seo_error_date_format_year
                self.set_status_color(wx.RED)

        # Check article image disk path
        # TODO check that image and menu image files have correct size, if something wrong set a special warning image
        if not self._article_full_image_path:
            # TODO set missing image
            self.set_status_color(wx.RED)

        # Check article image thumbnail disk path
        if not self._article_thumbnail_image_path:
            # TODO set missing image
            self.set_status_color(wx.RED)

        # Check article image caption
        if len(self._article_image_caption) < Numbers.article_image_caption_min or len(
                self._article_image_caption) > Numbers.article_image_caption_max:
            self._caption_error_message = Strings.seo_error_image_caption_length
            self.set_status_color(wx.RED)

        if self._article_image_caption == Strings.label_article_image_caption:
            self._date_error_message = Strings.seo_error_date_format
            self.set_status_color(wx.RED)

        # Check article image link title
        if len(self._article_image_link_title) < Numbers.article_image_title_min or len(
                self._article_image_link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            self.set_status_color(wx.RED)

        if self._article_image_link_title == Strings.label_article_image_link_title:
            self._link_title_error_message = Strings.seo_error_default_value
            self.set_status_color(wx.RED)

        # Check article image alt
        if len(self._article_image_alt) < Numbers.article_image_alt_min or len(
                self._article_image_alt) > Numbers.article_image_alt_max:
            self._image_alt_error_message = Strings.seo_error_image_alt_length
            self.set_status_color(wx.RED)

        if self._article_image_alt == Strings.label_article_image_alt:
            self._image_alt_error_message = Strings.seo_error_default_value
            self.set_status_color(wx.RED)

        # Test menu item
        print(self._menu_item)

    def _determine_menu_section_and_menu_item(self):
        """
        Find out which menu this article belongs in.
        :return: None
        :raises WrongFormatException: If the article is not found in any menu.
        """
        for menu in self._menus.values():
            self._menu_item = menu.find_item_by_file_name(self.get_filename())
            if self._menu_item:
                self._menu_section = menu
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

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_date(self) -> (str, str):
        """
        Return the article creation date and error to display in gui if there is one.
        :return: Return article creation date and error to display in gui if there is one.
        """
        return self._date, self._date_error_message

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

    def get_article_image_caption(self) -> (str, str):
        """
        Return the caption of the main article image and error to display in gui if there is one.
        :return: Return the caption of the main article image and error to display in gui if there is one.
        """
        return self._article_image_caption, self._caption_error_message

    def get_article_image_link_title(self) -> (str, str):
        """
        Return the link title of the main article image and error to display in gui if there is one.
        :return: Return the link title of the main article image and error to display in gui if there is one.
        """
        return self._article_image_link_title, self._link_title_error_message

    def get_article_image_alt(self) -> (str, str):
        """
        Return the alt description of the main article image and error to display in gui if there is one.
        :return: Return the alt description of the main article image and error to display in gui if there is one.
        """
        return self._article_image_alt, self._image_alt_error_message

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

    def get_menu_section(self) -> WhitebearDocumentMenu:
        """
        Return to which menu section this article belongs.
        :return: Return to which menu section this article belongs.
        """
        return self._menu_section

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
