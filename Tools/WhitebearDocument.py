from typing import List

from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Strings import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
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
        self._name = name
        self._path = path
        self._file_type = file_type
        self._parsed_html = None
        self._modified = False
        self._title = None
        self._description = None
        self._keywords = None
        self._date = None
        self._valid = False

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        """
        # Only parse if not parsed already and only if the document is valid.
        if not self._parsed_html and self.is_valid():

            pass

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

    def get_name(self) -> str:
        """
        Return the file name.
        :return: Return the file name.
        """
        return self._name

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

    def get_title(self) -> str:
        """
        Return the title of the web page.
        :return: Return the title of the web page.
        """
        return self._title

    def get_description(self) -> str:
        """
        Return the description of the web page.
        :return: Return the description of the web page.
        """
        return self._description

    def get_keywords(self) -> str:
        """
        Return the keywords of the web page.
        :return: Return the keywords of the web page.
        """
        return self._keywords

    def set_title(self, title: str) -> None:
        """
        Set the new title of the web page.
        Change modified attribute to True.
        :param title: New title for the web page.
        :return: None
        """
        self._title = title
        self.set_modified(True)

    def set_description(self, description: str) -> None:
        """
        Set the new description of the web page.
        Change modified attribute to True.
        :param description: New description for the web page.
        :return: None
        """
        self._description = description
        self.set_modified(True)

    def set_keywords(self, keywords: str) -> None:
        """
        Set the new keywords of the web page.
        Change modified attribute to True.
        :param keywords: New keywords for the web page.
        :return: None
        """
        self._keywords = keywords
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

    def set_name(self, name: str) -> None:
        """
        Set the new name for the file.
        Change modified attribute to True.
        :param name: New name for the file.
        :return: None
        """
        self._name = name
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

    def __str__(self) -> str:
        return "White bear file {}, Type {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}". \
            format(self.get_name(), self._string_type(), self.is_modified(), self.get_path(), self.get_title(),
                   self.get_keywords(), self.get_description())

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
