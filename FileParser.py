from typing import Tuple, List
from Exceptions.WrongFormatException import WrongFormatException
from ParsedFile import ParsedFile
from Constants.Strings import Strings
from bs4 import BeautifulSoup


class FileParser:
    """
    """

    # name_path is a syntax for unpacking a tuple
    def parse_file(self, name_path: Tuple[str, str]) -> ParsedFile:
        """Parse a file which is a whitebear html file. Identify the file type and create an object representing the
        file.
        :param name_path: Tuple (filename, file path).
        :return: ParsedFile instance containing the contents of the file.
        """
        file_name: str
        file_path: str
        file_name, file_path = name_path
        # Open file and pass file handle to beautiful soup.
        with open(file_path, 'r') as html:
            parsed_html: BeautifulSoup = BeautifulSoup(html, 'html5lib')

        file_type: int = self.__find_type(parsed_html)
        if file_type != ParsedFile.TYPE_OTHER:
            # This will be a regular kind of web site
            # TODO
            pass
        else:
            # This will be something special, normal text,...
            # TODO
            pass

    def __find_type(self, parsed_html):
        """Find out the type of the parsed file and return a constant representing the type.
        :param parsed_html: File parsed by beautifulsoup.
        :return: Int constant representing the file type.
        """
        if self.__is_article(parsed_html):
            return ParsedFile.TYPE_ARTICLE
        elif self.__is_menu(parsed_html):
            return ParsedFile.TYPE_MENU
        elif self.__is_index(parsed_html):
            return ParsedFile.TYPE_INDEX
        else:
            return ParsedFile.TYPE_OTHER

    @staticmethod
    def __is_article(parsed_html):
        """Return True if the parsed file is a whitebear article html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear article html.
        """
        if len(parsed_html.findAll('main', id="article")) != 1:
            return False
        return True

    @staticmethod
    def __is_menu(parsed_html):
        """Return True if the parsed file is a whitebear menu html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear menu html.
        """
        if len(parsed_html.findAll('main', id="menu")) != 1:
            return False
        return True

    @staticmethod
    def __is_index(parsed_html):
        """Return True if the parsed file is a whitebear index page html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear index page html.
        """
        if len(parsed_html.findAll('main', id="index")) != 1:
            return False
        return True

    @staticmethod
    def __is_css(parsed_html):
        """Return True if the parsed file is a website css stylesheet.
        :param parsed_html:
        :return: True if the parsed file is a whitebear css stylesheet.
        """
        raise NotImplemented('Not yet implemented')
