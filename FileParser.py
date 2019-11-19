from typing import Tuple, List
from Exceptions.WrongFormatException import WrongFormatException
from ParsedFile import ParsedFile
from Strings.Strings import Strings
from bs4 import BeautifulSoup


class FileParser:
    """
    """

    # name_path is a syntax for unpacking a tuple
    def create(self, name_path: Tuple[str, str]) -> ParsedFile:
        """Parse a file which is a whitebear html file. Identify the file type and create an object representing the
        file.
        :param name_path: Tuple (filename, file path).
        :return: ParsedFile instance containing the contents of the file.
        """
        file_name: str
        file_path: str
        file_name, file_path = name_path
        # Open file and pass file handle to beautiful soap.
        with open(file_path, 'r') as html:
            parsed_html: BeautifulSoup = BeautifulSoup(html, 'html5lib')
        # TODO ---------------------------------------
        return self.__parse_file(parsed_html, file_name)

    def __parse_file(self, parsed_html: BeautifulSoup, file_name: str, file_path: str) -> ParsedFile:
        """
        :raises WrongFormatException
        :param parsed_html:
        :return:
        """
        file_type: int = self.__find_type(parsed_html)
        if file_type != ParsedFile.TYPE_OTHER:
            # Set title
            if len(parsed_html.find_all('title')) != 1:
                raise WrongFormatException(Strings.exception_only_one_title_allowed + ' ' + file_name)
            else:
                # Finds first occurrence, but there is only one anyway at this point
                title: str = parsed_html.title.string

            # Set description
            meta_tags = parsed_html.find_all('meta')
            description = ''
            for tag in meta_tags:
                try:
                    if tag['name'] == 'description':
                        description: str = tag['content']
                except KeyError:
                    continue
            # No description found
            if not description:
                raise WrongFormatException(Strings.exception_meta_description_twice + ' ' + file_name)

        html_file_object.set_title(title)
        html_file_object.set_description(description)
        html_file_object.set_keywords(keywords)

    def __find_type(self, parsed_html):
        """Find out the type of the parsed file and return a constant representing the type.
        :param parsed_html: File parsed by beautifulsoup.
        :return: Int constant representing the file type.
        """
        if self.__is_article(parsed_html):
            return ParsedFile.TYPE_ARTICLE
        elif self.__is_menu(parsed_html):
            return ParsedFile.TYPE_MENU
        elif self.__is_gallery(parsed_html):
            return ParsedFile.TYPE_GALLERY
        elif self.__is_misc(parsed_html):
            return ParsedFile.TYPE_MISC
        elif self.__is_contact(parsed_html):
            return ParsedFile.TYPE_CONTACT
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
    def __is_gallery(parsed_html):
        """Return True if the parsed file is a whitebear gallery html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear gallery html.
        """
        if len(parsed_html.findAll('article', id="main", class_="wholePage")) != 1:
            return False
        if len(parsed_html.findAll('div', id="gallery")) != 1:
            return False
        return True

    @staticmethod
    def __is_misc(parsed_html):
        """Return True if the parsed file is a whitebear misc html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear misc html.
        """
        if len(parsed_html.findAll('main', id="misc")) != 1:
            return False
        return True

    @staticmethod
    def __is_contact(parsed_html):
        """Return True if the parsed file is a whitebear contact page html.
        :param parsed_html: File parsed by beautifulsoup.
        :return: True if the parsed file is a whitebear contact page html.
        """
        if len(parsed_html.findAll('main', id="contact")) != 1:
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
