from typing import List

import wx
from bs4 import BeautifulSoup
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Strings import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Exceptions.WrongFormatException import WrongFormatException
from Resources.Fetch import Fetch


class WhitebearDocument:
    """
    This class represents a file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    TYPE_INDEX = 0
    TYPE_ARTICLE = 1
    TYPE_MENU = 3
    TYPE_CSS = 4

    def __init__(self, name, path, file_type):
        """
        Create a new ParsedFile object.
        :param name: Name of the parsed file.
        :param path: Full path on disk to the parsed file
        :param file_type: Type of the parsed file. Can be one of ParsedFile.TYPE_... types
        """
        # File properties
        self._file_name = name
        self._path = path
        self._file_type = file_type
        self._modified = False
        self._valid = False

        # Article data
        self._parsed_html = None
        self._date = None
        self._article_name = None
        self._meta_keywords = None
        self._meta_description = None
        # Article image data
        self._article_image_path = None
        self._article_image = None
        self._article_image_caption = None
        self._article_image_link_title = None
        self._article_image_alt = None
        # Menu item data
        self._menu_image_path = None
        self._menu_image = None
        self._menu_item_name = None
        self._menu_image_alt = None
        self._menu_image_link_title = None

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Only parse if not parsed already and only if the document is valid.
        if not self._parsed_html and self.is_valid():
            self._get_parsed_html()
            if self.get_type() == WhitebearDocument.TYPE_ARTICLE:
                self._parse_meta_description()
                self._parse_meta_keywords()
                self._parse_date()

    def _parse_meta_description(self):
        """
        Parse the meta description of this document and save it into an instance variable.
        :return: None
        :raises WrongFormatException: if there are more than one description tags.
        """
        description = self._parsed_html.find_all(name='meta', attrs={'name': 'description', 'content': True})
        if len(description) == 1:
            self._meta_description = description[0]['content']
        else:
            raise WrongFormatException(Strings.exception_parse_multiple_descriptions)

    def _parse_meta_keywords(self):
        """
        Parse the meta keywords of this document and save it into an instance variable.
        :return: None
        :raises WrongFormatException: if there are more than one keywords tags.
        """
        keywords = self._parsed_html.find_all(name='meta', attrs={'name': 'keywords', 'content': True})
        if len(keywords) == 1:
            self._meta_keywords = keywords[0]['content']
        else:
            raise WrongFormatException(Strings.exception_parse_multiple_keywords)

    def _parse_date(self):
        """
        Parse the date stamp of this document and save it into an instance variable.
        :return: None
        """
        date = self._parsed_html.find_all(name='p', attrs={'id': 'date'})[0].string
        self._date = date if date else ''

    def _parse_article_name(self):
        """
        Parse the name of this article and save it into an instance variable.
        :return: None
        """
        # TODO this
        date = self._parsed_html.find_all(name='p', attrs={'id': 'date'})[0].string
        self._date = date if date else ''

    def _get_parsed_html(self):
        """
        Parse this document's html with bs4 and save it to an instance variable.
        :return: None
        """
        with open(self._path, 'r') as document:
            contents = document.read()
            self._parsed_html = BeautifulSoup(contents, 'html5lib')

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the correct xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        xmlschema = None
        errors = []
        try:
            if self.is_article():
                xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_article.xsd')))
            elif self.is_menu():
                xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_menu.xsd')))
            elif self.is_index():
                xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_index.xsd')))
            else:
                # TODO validate css
                pass
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

    # Boolean functions ------------------------------------------------------------------------------------------------
    def is_valid(self) -> bool:
        """
        Return True if this document is valid according to xml schema.
        :return: True if this document is valid according to xml schema.
        """
        return self._valid

    def is_modified(self) -> bool:
        """
        Return True if this file was modified in the editor.
        :return: True if this file was modified in the editor.
        """
        return self._modified

    def is_article(self) -> bool:
        """
        Return True if this file is of type ParsedFile.TYPE_ARTICLE.
        :return: True if this file is of type ParsedFile.TYPE_ARTICLE.
        """
        if self._file_type == self.TYPE_ARTICLE:
            return True
        return False

    def is_css(self) -> bool:
        """
        Return True if this file is of type ParsedFile.TYPE_CSS.
        :return: True if this file is of type ParsedFile.TYPE_CSS.
        """
        if self._file_type == self.TYPE_CSS:
            return True
        return False

    def is_menu(self) -> bool:
        """
        Return True if this file is of type ParsedFile.TYPE_MENU.
        :return: True if this file is of type ParsedFile.TYPE_MENU.
        """
        if self._file_type == self.TYPE_MENU:
            return True
        return False

    def is_index(self) -> bool:
        """
        Return True if this file is of type ParsedFile.TYPE_INDEX.
        :return: True if this file is of type ParsedFile.TYPE_INDEX.
        """
        if self._file_type == self.TYPE_INDEX:
            return True
        return False

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_filename(self) -> str:
        """
        Return the file name.
        :return: Return the file name.
        """
        return self._file_name

    def get_date(self) -> str:
        """
        Return the article creation date.
        :return: Return article creation date.
        """
        return self._date

    def get_path(self) -> str:
        """
        Return the full file path on disk.
        :return: Return the full file path on disk.
        """
        return self._path

    def get_parsed_html(self):
        """
        Return the parsed html contents.
        :return: Return the parsed html contents.
        """
        return self._parsed_html

    def get_type(self) -> int:
        """
        Return the file type.
        :return: Return the file type.
        """
        return self._file_type

    def get_article_name(self) -> str:
        """
        Return the name of the article.
        :return: Return the name of the article.
        """
        return self._article_name

    def get_description(self) -> str:
        """
        Return the description of the web page.
        :return: Return the description of the web page.
        """
        return self._meta_description

    def get_keywords(self) -> str:
        """
        Return the keywords of the web page.
        :return: Return the keywords of the web page.
        """
        return self._meta_keywords

    def get_article_image_path(self) -> str:
        """
        Return the path to the article image full version.
        :return: Return the path to the article image full version.
        """
        return self._article_image_path

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

    def get_menu_image_path(self) -> str:
        """
        Return the path to the menu image.
        :return: Return the path to the menu image.
        """
        return self._menu_image_path

    def get_menu_image(self) -> wx.Image:
        """
        Return the menu image wx image instance.
        :return: Return the menu image wx image instance.
        """
        return self._menu_image

    def get_menu_item_name(self) -> str:
        """
        Return the name of the menu item associate with this article.
        :return: Return the name of the menu item associate with this article.
        """
        return self._menu_item_name

    def get_menu_image_link_title(self) -> str:
        """
        Return the link title of the menu image.
        :return: Return the link title of the menu image.
        """
        return self._menu_image_link_title

    def get_menu_image_alt(self) -> str:
        """
        Return the alt description of the menu image.
        :return: Return the alt description of the menu image.
        """
        return self._menu_image_alt

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_article_name(self, name: str) -> None:
        """
        Set the new article name on the web page.
        Change modified attribute to True.
        :param name: New article name for the web page.
        :return: None
        """
        self._article_name = name
        self.set_modified(True)

    def set_description(self, description: str) -> None:
        """
        Set the new description of the web page.
        Change modified attribute to True.
        :param description: New description for the web page.
        :return: None
        """
        self._meta_description = description
        self.set_modified(True)

    def set_keywords(self, keywords: str) -> None:
        """
        Set the new keywords of the web page.
        Change modified attribute to True.
        :param keywords: New keywords for the web page.
        :return: None
        """
        self._meta_keywords = keywords
        self.set_modified(True)

    def set_parsed_html(self, parsed_html) -> None:
        """
        Set the new parsed html contents of the web page.
        Change modified attribute to True.
        :param parsed_html: New parsed html contents of the web page.
        :return: None
        """
        self._parsed_html = parsed_html
        self.set_modified(True)

    def set_modified(self, modified: bool) -> None:
        """
        Set the modified attribute.
        :raises TypeError if the new modified parameter is not bool.
        :param modified: New modified attribute state.
        :return: None
        """
        self._modified = modified

    def set_filename(self, name: str) -> None:
        """
        Set the new name for the file.
        Change modified attribute to True.
        :param name: New name for the file.
        :return: None
        """
        self._file_name = name
        self.set_modified(True)

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
        self._article_image_path = path
        self.set_modified(True)

    def set_article_image(self, image: wx.Image) -> None:
        """
        Set the new main article image.
        Change modified attribute to True.
        :param image: New wx.Image.
        :return: None
        """
        self._article_image = image
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

    def set_menu_image_path(self, path: str) -> None:
        """
        Set the new menu image path for this article.
        Change modified attribute to True.
        :param path: New image path in disk.
        :return: None
        """
        self._menu_image_path = path
        self.set_modified(True)

    def set_menu_image(self, image: wx.Image) -> None:
        """
        Set the new menu image.
        Change modified attribute to True.
        :param image: New wx.Image.
        :return: None
        """
        self._menu_image = image
        self.set_modified(True)

    def set_menu_item_name(self, text: str) -> None:
        """
        Set the new menu item name for this article.
        Change modified attribute to True.
        :param text: New manu item name.
        :return: None
        """
        self._menu_item_name = text
        self.set_modified(True)

    def set_menu_image_link_title(self, text: str) -> None:
        """
        Set the new menu image image link title.
        Change modified attribute to True.
        :param text: New image link title.
        :return: None
        """
        self._menu_image_link_title = text
        self.set_modified(True)

    def set_menu_image_alt(self, text: str) -> None:
        """
        Set the new menu image alt description.
        Change modified attribute to True.
        :param text: New image alt description.
        :return: None
        """
        self._menu_image_alt = text
        self.set_modified(True)

    def __str__(self) -> str:
        return "White bear file {}, Type {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}". \
            format(self.get_filename(), self._string_type(), self.is_modified(), self.get_path(),
                   self.get_article_name(), self.get_keywords(), self.get_description())

    def _string_type(self):
        """
        Return a string human readable file type description.
        :return: A string human readable file type description.
        """
        if self.is_article():
            return "article"
        elif self.is_menu():
            return "menu"
        elif self.is_css():
            return "css"
        elif self.is_index():
            return "index"
        else:
            return "other"
