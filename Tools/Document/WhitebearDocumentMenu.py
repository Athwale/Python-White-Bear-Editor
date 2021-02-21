import os
from typing import List

from bs4 import BeautifulSoup
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

from Constants.Constants import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Resources.Fetch import Fetch
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Tools import Tools


class WhitebearDocumentMenu(WhitebearDocument):
    """
    This class represents a menu file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str):
        """
        Create a new WhitebearDocumentMenuIndex object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        """
        # File properties are in base class
        super().__init__(name, path)
        self._menu_items = []
        self.parse_self()

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # In case of menu, we create the instances only if the source file is valid and we only parse them once.
        super(WhitebearDocumentMenu, self).parse_self()
        self._parse_page_name()
        self._parse_menu_items()

    def _parse_menu_items(self) -> None:
        """
        Parse the menu items of this menu and save them into an instance variable. Image path is None if the file
        is not on hard drive.
        :return: None
        """
        self._menu_items.clear()
        menu_container = self._parsed_html.find(name='nav', attrs={'class': 'sixItems'})
        divs = menu_container.find_all(name='div', attrs={'class': 'link'})
        for div in divs:
            href = div.a['href']
            title = div.a['title']
            full_image_path = os.path.join(self._working_directory, div.img['src'])
            image_alt = div.img['alt']
            string_content = div.p.strings
            name = ''.join(string_content)

            if not os.path.exists(full_image_path) or not os.access(full_image_path, os.R_OK) or not os.access(
                    full_image_path, os.W_OK):
                full_image_path = None

            self._menu_items.append(MenuItem(name.lower(), name, title, image_alt, href, full_image_path,
                                             div.img['src']))

    def _parse_page_name(self) -> None:
        """
        Parse the name of this menu and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'menuPage'})
        self._page_name = article.h2.string

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the article xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        with open(self.get_path(), 'r') as file:
            html_string = file.read()
        self._valid, errors = Tools.validate(html_string, 'schema_menu.xsd')
        return self._valid, errors

    def convert_to_html(self) -> str:
        """
        Converts this document into a html white bear menu page.
        :return: The converted html in a string.
        :raise UnrecognizedFileException if template file can not be validated.
        :raise UnrecognizedFileException if html parse fails.
        :raise UnrecognizedFileException if generated html fails validation.
        """
        with open(Fetch.get_resource_path('menu_template.html'), 'r') as template:
            template_string = template.read()
        is_valid, errors = Tools.validate(template_string, 'schema_menu_template.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + 'menu_template.html ' +
                                            str(errors))

        parsed_template = BeautifulSoup(template_string, 'html5lib')
        print('c')

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_menu_items(self) -> List[MenuItem]:
        """
        Return a list of MenuItem of all menu items of this menu.
        :return: A list of [MenuItem,...]
        """
        return self._menu_items

    def get_section_name(self) -> str:
        """
        Return the name of the menu section which is identical to the main title but lowercase in this case.
        :return: Return the name of the menu section.
        """
        return self.get_page_name()[0].lower()

    def find_item_by_file_name(self, file_name: str):
        """
        Return a MenuItem that contains a link to the file_name, only one must exist. None if not found.
        :param file_name: Name of the website to find in this menu.
        :return: Return a MenuItem that contains a link to the file_name, only one must exist. None if not found.
        """
        for item in self._menu_items:
            if file_name == item.get_link_href():
                return item
        return None

    # Setters ----------------------------------------------------------------------------------------------------------
