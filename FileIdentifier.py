from bs4 import BeautifulSoup
import os
from HtmlFile import HtmlFile


class FileIdentifier:
    """This class contains methods that parse or
    help with parsing the white bear specific html files.

    """
    def create(self, file_path):
        """Parse files which are white bear html files. Identify the file types and create an object representing the
        file and set basic attributes.
        :param file_path:
        :return:
        """
        # Open file and pass file handle to beautiful soap.
        with open(file_path, "r") as html:
            parsed = BeautifulSoup(html, "html5lib")

        file_name = os.path.basename(file_path)
        file_type = self.__get_type(parsed)
        return HtmlFile(file_name, file_path, file_type, parsed)

    def __get_type(self, parsed):
        """

        :param parsed:
        :return:
        """
        if self.__is_article(parsed):
            return HtmlFile.TYPE_ARTICLE
        elif self.__is_menu(parsed):
            return HtmlFile.TYPE_MENU
        elif self.__is_gallery(parsed):
            return HtmlFile.TYPE_GALLERY
        elif self.__is_misc(parsed):
            return HtmlFile.TYPE_MISC
        elif self.__is_contact(parsed):
            return HtmlFile.TYPE_CONTACT
        elif self.__is_index(parsed):
            return HtmlFile.TYPE_INDEX
        else:
            return HtmlFile.TYPE_OTHER

    @staticmethod
    def __is_article(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('main', id="article")) != 1:
            return False
        return True

    @staticmethod
    def __is_menu(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('main', id="menu")) != 1:
            return False
        return True

    @staticmethod
    def __is_gallery(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('article', id="main", class_="wholePage")) != 1:
            return False
        if len(parsed.findAll('div', id="gallery")) != 1:
            return False
        return True

    @staticmethod
    def __is_misc(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('main', id="misc")) != 1:
            return False
        return True

    @staticmethod
    def __is_contact(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('main', id="contact")) != 1:
            return False
        return True

    @staticmethod
    def __is_index(parsed):
        """

        :param parsed:
        :return:
        """
        if len(parsed.findAll('main', id="index")) != 1:
            return False
        return True
