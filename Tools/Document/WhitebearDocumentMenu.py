import os
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag

from Constants.Constants import Strings, Numbers
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

    def __init__(self, path: str, menus):
        """
        Create a new WhitebearDocumentMenuIndex object.
        :param path: Full disk path to the file.
        :param menus: A dictionary of page_name: WhitebearDocumentMenu containing all parsed menus.
        """
        # File properties are in base class
        super().__init__(path)
        self._menu_items = []
        self._menus = menus

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        # In case of menu, we create the instances only if the source file is valid, and we only parse them once.
        super(WhitebearDocumentMenu, self).parse_self()
        self._parse_page_name()
        self._parse_menu_items()
        self.test_self()

    def test_self(self) -> bool:
        """
        Perform a SEO test on this document.
        :return: True if seo test passed.
        """
        # Check name, meta keywords and description
        # Menu items are seo tested by articles.
        super(WhitebearDocumentMenu, self).test_self_basic()

        # Check page name length must be at least 3 and must not be default.
        name_result, message, color = self.seo_test_name(self._page_name)
        # Message may contain OK if seo passed.
        self._page_name_error_message = message
        if not name_result:
            self.set_status_color(color)

        if self.get_status_color() == Numbers.RED_COLOR:
            return False
        return True

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

            self._menu_items.append(MenuItem(name, title, image_alt, href, full_image_path, div.img['src']))

    def _parse_page_name(self) -> None:
        """
        Parse the name of this menu and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'menuPage'})
        name = article.h2.string
        if name:
            self._page_name = str(name)
        else:
            self._page_name = ''

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

    def convert_to_html(self) -> None:
        """
        Converts this document into a html white bear menu page.
        :return: None
        :raise UnrecognizedFileException if template file can not be validated.
        :raise UnrecognizedFileException if html parse fails.
        :raise UnrecognizedFileException if generated html fails validation.
        :raises UnrecognizedFileException if xml schema is incorrect.
        """
        with open(Fetch.get_resource_path('menu_template.html'), 'r') as template:
            template_string = template.read()
        is_valid, errors = Tools.validate(template_string, 'schema_menu_template.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + 'menu_template.html ' +
                                            str(errors))

        parsed_template = BeautifulSoup(template_string, 'html5lib')

        # Fill title.
        title: Tag = parsed_template.find(name='title')
        title.string = Strings.menu_title_stump + ' ' + self._page_name + ' | ' + Strings.page_name

        # Fill description.
        description = parsed_template.find_all(name='meta', attrs={'name': 'description', 'content': True})
        if len(description) == 1:
            description[0]['content'] = self._meta_description
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_descriptions)

        # Fill keywords.
        keywords = parsed_template.find_all(name='meta', attrs={'name': 'keywords', 'content': True})
        if len(keywords) == 1:
            keywords[0]['content'] = ', '.join(self._meta_keywords)
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_keywords)

        # Fill author.
        author = parsed_template.find_all(name='meta', attrs={'name': 'author', 'content': True})
        if len(author) == 1:
            author[0]['content'] = self._config_manager.get_author()
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_authors)

        # Fill script.
        script = parsed_template.find(name='script')
        script.string = self._config_manager.get_script()

        # Fill global title.
        figure = parsed_template.find(name='header').figure
        figure.figcaption.string = self._config_manager.get_global_title()
        heading = parsed_template.find(name='h1', attrs={'id': 'heading'})
        heading.string = self._config_manager.get_global_title()

        # Activate correct menu, generate menu items according to menus.
        menu_container = parsed_template.find(name='nav')
        for instance in sorted(self._menus.values(), key=lambda x: x.get_section_name(), reverse=True):
            new_item = parsed_template.new_tag('a', attrs={'class': 'menu', 'href': instance.get_filename(),
                                                           'title': instance.get_page_name()[0]})
            new_item.string = instance.get_page_name()[0]
            if instance.get_filename() == self._file_name:
                new_item['id'] = 'active'
            menu_container.append(new_item)

        # Fill main page title.
        article = parsed_template.find(name='article', attrs={'class': 'menuPage'})
        article.h2.string = self._page_name

        # Fill menu items.
        menu_container = parsed_template.find(name='nav', attrs={'class': 'sixItems'})
        for item in self._menu_items:
            item: MenuItem
            attrs = {'class': 'link'}
            if not item.get_article():
                # Skip deleted articles.
                continue
            if not item.get_article().test_self(self._config_manager.get_online_test()):
                # Hide this menu item because this article is not yet finished or is deleted. The item will be available
                # for future parsing though so the editor will load the menu item correctly for the unfinished article.
                attrs['class'] = 'link hidden'
            new_div = parsed_template.new_tag('div', attrs=attrs)
            href = item.get_link_href()
            title = item.get_link_title()[0]
            width = item.get_image_size()[0]
            height = item.get_image_size()[1]
            src = item.get_filename()
            alt = item.get_image_alt()[0]
            text = item.get_article_name()[0]
            new_a = parsed_template.new_tag('a', attrs={'href': href, 'title': title})
            new_img = parsed_template.new_tag('img', attrs={'width': width, 'height': height, 'src': src, 'alt': alt})
            new_p = parsed_template.new_tag('p')
            new_p.string = text

            new_a.append(new_img)
            new_div.append(new_a)
            new_div.append(new_p)
            menu_container.append(new_div)

        output = str(parsed_template)
        is_valid, errors = Tools.validate(output, 'schema_menu.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_bug + '\n' + self.get_filename() + ' \n' + str(errors))

        self._html = output

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_html_to_save(self) -> str:
        """
        Returns the last converted string HTML code of this article. Run convert_to_html() before calling this method.
        :return: String HTML of the article or none if the document was not converted yet.
        """
        return self._html

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
    def add_item(self, item: MenuItem) -> None:
        """
        Add a new item into the menu,
        :param item: The new item.
        :return: None
        """
        self._menu_items.append(item)
        self.set_modified(True)
