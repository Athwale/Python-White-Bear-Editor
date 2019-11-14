from bs4 import BeautifulSoup
import os
from ParsedFile import ParsedFile


class FileIdentifier:
    """This class contains methods that parse or help with parsing the white bear specific html files.
    """

    def create(self, file_path):
        """Parse a file which is a whitebear html file. Identify the file type and create an object representing the
        file + set basic attributes.
        :param file_path: Full path to the file on the system.
        :return: ParsedFile instance containing the contents of the file.
        """
        # Open file and pass file handle to beautiful soap.
        with open(file_path, "r") as html:
            parsed = BeautifulSoup(html, "html5lib")

        file_name = os.path.basename(file_path)
        file_type = self.__get_type(parsed)
        return ParsedFile(file_name, file_path, file_type, parsed)

    def __get_type(self, parsed):
        """Find out the type of the parsed file and return a constant representing the type.
        :param parsed: File parsed by beautifulsoup.
        :return: Int constant representing the file type.
        """
        if self.__is_article(parsed):
            return ParsedFile.TYPE_ARTICLE
        elif self.__is_menu(parsed):
            return ParsedFile.TYPE_MENU
        elif self.__is_gallery(parsed):
            return ParsedFile.TYPE_GALLERY
        elif self.__is_misc(parsed):
            return ParsedFile.TYPE_MISC
        elif self.__is_contact(parsed):
            return ParsedFile.TYPE_CONTACT
        elif self.__is_index(parsed):
            return ParsedFile.TYPE_INDEX
        else:
            return ParsedFile.TYPE_OTHER

    @staticmethod
    def __is_article(parsed):
        """Return True if the parsed file is a whitebear article html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear article html.
        """
        if len(parsed.findAll('main', id="article")) != 1:
            return False
        return True

    @staticmethod
    def __is_menu(parsed):
        """Return True if the parsed file is a whitebear menu html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear menu html.
        """
        if len(parsed.findAll('main', id="menu")) != 1:
            return False
        return True

    @staticmethod
    def __is_gallery(parsed):
        """Return True if the parsed file is a whitebear gallery html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear gallery html.
        """
        if len(parsed.findAll('article', id="main", class_="wholePage")) != 1:
            return False
        if len(parsed.findAll('div', id="gallery")) != 1:
            return False
        return True

    @staticmethod
    def __is_misc(parsed):
        """Return True if the parsed file is a whitebear misc html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear misc html.
        """
        if len(parsed.findAll('main', id="misc")) != 1:
            return False
        return True

    @staticmethod
    def __is_contact(parsed):
        """Return True if the parsed file is a whitebear contact page html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear contact page html.
        """
        if len(parsed.findAll('main', id="contact")) != 1:
            return False
        return True

    @staticmethod
    def __is_index(parsed):
        """Return True if the parsed file is a whitebear index page html.
        :param parsed: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear index page html.
        """
        if len(parsed.findAll('main', id="index")) != 1:
            return False
        return True

    @staticmethod
    def __is_css(parsed):
        """Return True if the parsed file is a website css stylesheet.
        :param parsed:
        :return: True if the parsed file is a whitebear css stylesheet.
        """
        raise NotImplemented('Not yet implemented')

