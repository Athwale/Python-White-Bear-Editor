import os

import htmlmin
import wx
from bs4 import BeautifulSoup

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Exceptions.WrongFormatException import WrongFormatException
from Tools.ConfigManager import ConfigManager
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter


class WhitebearDocument:
    """
    This class represents a file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation. This is a base class with only the common information for all pages.
    """

    def __init__(self, path: str):
        """
        Create a new WhitebearDocument object.
        :param path: Full path on disk to the file
        """
        # File properties
        self._file_name = os.path.basename(path)
        self._path = path
        self._working_directory = os.path.dirname(path)
        self._modified = False
        # We create instances of documents after validation, so we already know they are valid.
        self._valid = True
        self._status_color = None
        self._config_manager: ConfigManager = ConfigManager.get_instance()
        # TODO spellcheck as separate method runs once on document check.
        self._spellchecker = SpellChecker(self._config_manager.get_spelling_lang(), filters=[EmailFilter, URLFilter])

        # Page data
        self._parsed_html = None
        self._page_name: str = ''
        self._page_name_error_message: str = ''
        self._meta_keywords: str = ''
        self._keywords_error_message: str = ''
        self._meta_description: str = ''
        self._description_error_message: str = ''

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content. Only call this after the subclass has validated
        itself.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Reset color when we reparse from disk.
        self._status_color = None
        self._get_parsed_html()
        self._parse_meta_description()
        self._parse_meta_keywords()

    def _parse_meta_description(self) -> None:
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

    def _parse_meta_keywords(self) -> None:
        """
        Parse the meta keywords of this document and save it into an instance variable.
        :return: None
        :raises WrongFormatException: if there are more than one keyword tags.
        """
        keywords = self._parsed_html.find_all(name='meta', attrs={'name': 'keywords', 'content': True})
        if len(keywords) == 1:
            self._meta_keywords = [word.strip() for word in keywords[0]['content'].split(',')]
        else:
            raise WrongFormatException(Strings.exception_parse_multiple_keywords)

    def _get_parsed_html(self) -> None:
        """
        Parse this document's html with bs4 and save it to an instance variable.
        :return: None
        """
        with open(self._path, 'r') as document:
            contents = document.read()
            minimized = htmlmin.minify(contents, remove_empty_space=True, remove_comments=True)
            # Fix spaces around tags. Preserves &nbsp.
            minimized = minimized.replace('<p> ', '<p>')
            minimized = minimized.replace(' <p/>', '<p/>')
            minimized = minimized.replace('<br> ', '<br>')
            # Does not preserve &nbsp
            self._parsed_html = BeautifulSoup(minimized, 'html5lib')

    @staticmethod
    def seo_test_keywords(keywords: str) -> (bool, str, wx.Colour):
        """
        SEO test keywords and return False, error string and new status color if incorrect.
        :param keywords: The keywords to check.
        :return: Return False, error string and new status color if incorrect.
        """
        keywords_error_message = Strings.status_ok
        result = True
        color = Numbers.GREEN_COLOR
        keywords_length = 0
        if ',' not in keywords:
            keywords_error_message = Strings.seo_error_keywords_format
            result = False
        else:
            keywords_list = [word.strip() for word in keywords.split(',')]
            if len(keywords_list) < Numbers.min_keywords:
                keywords_error_message = Strings.seo_error_keywords_amount
                result = False
            else:
                for word in keywords_list:
                    keywords_length += len(word)
                if keywords_length < Numbers.keywords_min_length or keywords_length > Numbers.keywords_max_length:
                    keywords_error_message = Strings.seo_error_keywords_length
                    result = False

        if not result:
            color = Numbers.RED_COLOR
        return result, keywords_error_message, color

    @staticmethod
    def seo_test_description(description: str) -> (bool, str, wx.Colour):
        """
        SEO test description and return False, error string and new status color if incorrect.
        :param description: The description to check
        :return: Return False, error string and new status color if incorrect.
        """
        description_error_message = Strings.status_ok
        result = True
        color = Numbers.GREEN_COLOR
        if len(description) < Numbers.description_min_length or len(description) > Numbers.description_max_length:
            description_error_message = Strings.seo_error_description_length
            result = False

        if description == Strings.label_article_description:
            description_error_message = Strings.seo_error_default_value
            result = False

        if not result:
            color = Numbers.RED_COLOR
        return result, description_error_message, color

    @staticmethod
    def seo_test_name(name: str) -> (bool, str, wx.Colour):
        """
        SEO test article name and return False, error string and new status color if incorrect.
        :param name: The name to check
        :return: Return False, error string and new status color if incorrect.
        """
        page_name_error_message = Strings.status_ok
        result = True
        color = Numbers.GREEN_COLOR
        if len(name) < Numbers.article_name_min_length or len(name) > Numbers.article_name_max_length:
            page_name_error_message = Strings.seo_error_name_length
            result = False
        if name == Strings.label_article_title:
            page_name_error_message = Strings.seo_error_default_value
            result = False

        if not result:
            color = Numbers.RED_COLOR
        return result, page_name_error_message, color

    def seo_test_self_basic(self) -> bool:
        """
        Perform basic SEO self test and change internal instance state accordingly. If description or
        keywords are incorrect, change valid to False and the color of the file list item to red.
        Errors found in the validation are saved are then returned along with the data by getter methods.
        :return: False if seo test failed.
        """
        # Clear all error on each retest
        self._page_name_error_message: str = ''
        self._keywords_error_message: str = ''
        self._description_error_message: str = ''
        if not self._status_color:
            self._status_color = wx.WHITE

        # Check meta keywords
        keywords_result, message, color = self.seo_test_keywords(', '.join(self._meta_keywords))
        self._keywords_error_message = message
        if not keywords_result:
            self.set_status_color(color)

        # Check meta description
        description_result, message, color = self.seo_test_description(self._meta_description)
        self._description_error_message = message
        if not description_result:
            self.set_status_color(color)

        if self.get_status_color() == Numbers.RED_COLOR:
            return False
        return True

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

    def is_seo_ok(self) -> bool:
        """
        Returns True if the document passed last SEO check and does not have red status color.
        :return: True if the document passed last SEO check and does not have red status color.
        """
        return self._status_color != Numbers.RED_COLOR

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_filename(self) -> str:
        """
        Return the file name.
        :return: Return the file name.
        """
        return self._file_name

    def get_path(self) -> str:
        """
        Return the full file path on disk.
        :return: Return the full file path on disk.
        """
        return self._path

    def get_parsed_html(self) -> None:
        """
        Return the parsed html contents.
        :return: Return the parsed html contents.
        """
        return self._parsed_html

    def get_page_name(self) -> (str, str):
        """
        Return the name of the article and error to display in gui if there is one.
        :return: Return the name of the article and error to display in gui if there is one.
        """
        return self._page_name, self._page_name_error_message

    def get_description(self) -> (str, str):
        """
        Return the description of the web page and error to display in gui if there is one.
        :return: Return the description of the web page and error to display in gui if there is one.
        """
        return self._meta_description, self._description_error_message

    def get_keywords_string(self) -> (str, str):
        """
        Return the keywords of the web page and error to display in gui if there is one.
        :return: Return the keywords of the web page and error to display in gui if there is one.
        """
        return ', '.join(self._meta_keywords), self._keywords_error_message

    def get_keywords(self) -> (str, str):
        """
        Return the keywords of the web page as list and error to display in gui if there is one.
        :return: Return the keywords of the web page as list and error to display in gui if there is one.
        """
        return self._meta_keywords, self._keywords_error_message

    def get_working_directory(self) -> str:
        """
        Return the working directory where this document is stored.
        :return: Return the working directory where this document is stored.
        """
        return self._working_directory

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        :return: Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        """
        return self._status_color

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_page_name(self, name: str) -> bool:
        """
        Set the new article name on the web page.
        Change modified attribute to True.
        :param name: New article name for the web page.
        :return: True if name was changed.
        """
        if name != self._page_name:
            self._page_name = name
            self.set_modified(True)
            return True
        return False

    def set_description(self, description: str) -> None:
        """
        Set the new description of the web page.
        Change modified attribute to True.
        :param description: New description for the web page.
        :return: None
        """
        if self._meta_description != description:
            self._meta_description = description
            self.set_modified(True)

    def set_keywords(self, keywords: [str]) -> None:
        """
        Set the new keywords of the web page.
        Change modified attribute to True.
        :param keywords: New keywords list for the web page.
        :return: None
        """
        if self._meta_keywords != keywords:
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
        if modified and not self._status_color == Numbers.RED_COLOR:
            self.set_status_color(Numbers.BLUE_COLOR)

    def set_filename(self, name: str) -> None:
        """
        Set the new name for the file.
        Change modified attribute to True.
        :param name: New name for the file.
        :return: None
        """
        self._file_name = name
        self.set_modified(True)

    def set_status_color(self, new_color: wx.Colour) -> None:
        """
        Set new status color. If the color is red, set valid to False.
        :param new_color: New wx.Colour color.
        :return: None
        """
        self._status_color = new_color
        if new_color == Numbers.RED_COLOR:
            self._valid = False

    def __str__(self) -> str:
        return "White bear file {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}". \
            format(self.get_filename(), self.is_modified(), self.get_path(),
                   self.get_page_name(), self.get_keywords(), self.get_description())
