import os

from bs4 import BeautifulSoup

from Constants.Strings import Strings
from Exceptions.WrongFormatException import WrongFormatException


class WhitebearDocument:
    """
    This class represents a file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation. This is a base class with only the common information for all pages.
    """

    def __init__(self, name: str, path: str, menus):
        """
        Create a new WhitebearDocument object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        :param menus: A list of WhitebearDocuments representing menus
        """
        # File properties
        self._file_name = name
        self._path = path
        self._menus = menus
        self._working_directory = os.path.dirname(path)
        self._modified = False
        # We create instances of documents after validation so we already know they are valid.
        self._valid = True

        # Article data
        self._parsed_html = None
        self._page_name = None
        self._meta_keywords = None
        self._meta_description = None

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content. Only call this after the subclass has validated
        it self.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # Only parse if not parsed already and only if the document is valid.
        if not self._parsed_html:
            self._get_parsed_html()
            self._parse_meta_description()
            self._parse_meta_keywords()

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

    def _get_parsed_html(self):
        """
        Parse this document's html with bs4 and save it to an instance variable.
        :return: None
        """
        with open(self._path, 'r') as document:
            contents = document.read()
            self._parsed_html = BeautifulSoup(contents, 'html5lib')

    def seo_test_self_basic(self):
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

    def get_parsed_html(self):
        """
        Return the parsed html contents.
        :return: Return the parsed html contents.
        """
        return self._parsed_html

    def get_page_name(self) -> str:
        """
        Return the name of the article.
        :return: Return the name of the article.
        """
        return self._page_name

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

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_page_name(self, name: str) -> None:
        """
        Set the new article name on the web page.
        Change modified attribute to True.
        :param name: New article name for the web page.
        :return: None
        """
        self._page_name = name
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

    def __str__(self) -> str:
        return "White bear file {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}". \
            format(self.get_filename(), self.is_modified(), self.get_path(),
                   self.get_page_name(), self.get_keywords(), self.get_description())
