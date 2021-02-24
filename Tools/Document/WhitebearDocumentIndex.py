from typing import List, Dict

from bs4 import BeautifulSoup
from bs4.element import Tag

from Constants.Constants import Strings, Numbers
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Resources.Fetch import Fetch
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class WhitebearDocumentIndex(WhitebearDocument):
    """
    This class represents an index file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str, menus: Dict[str, WhitebearDocumentMenu], articles):
        """
        Create a new WhitebearDocument object.
        :param name: Name of the file.
        :param path: Full path on disk to the file.
        :param menus: A dictionary of WhitebearDocuments representing menus.
        :param articles: A dictionary of WhitebearDocuments representing other loaded articles.
        """
        # File properties are in base class
        super().__init__(name, path)
        self._menus = menus
        self._articles = articles
        self._html = None

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        super(WhitebearDocumentIndex, self).parse_self()
        self._parse_page_name()

    def _parse_page_name(self) -> None:
        """
        Parse the name of this article and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'indexPage'})
        self._page_name = article.h2.string

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the index xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        with open(self.get_path(), 'r') as file:
            html_string = file.read()
        self._valid, errors = Tools.validate(html_string, 'schema_index.xsd')
        return self._valid, errors

    def convert_to_html(self) -> None:
        """
        Converts this document into a html white bear article page.
        :return: None
        :raise UnrecognizedFileException if template file can not be validated.
        :raise UnrecognizedFileException if html parse fails.
        :raise UnrecognizedFileException if generated html fails validation.
        :raises UnrecognizedFileException if xml schema is incorrect.
        """
        config_manager: ConfigManager = ConfigManager.get_instance()
        with open(Fetch.get_resource_path('index_template.html'), 'r') as template:
            template_string = template.read()
        is_valid, errors = Tools.validate(template_string, 'schema_index_template.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + 'index_template.html ' +
                                            str(errors))

        parsed_template = BeautifulSoup(template_string, 'html5lib')

        # Fill title.
        title: Tag = parsed_template.find(name='title')
        title.string = self._page_name + ' | ' + config_manager.get_global_title()

        # Fill description.
        description = parsed_template.find_all(name='meta', attrs={'name': 'description', 'content': True})
        if len(description) == 1:
            description[0]['content'] = config_manager.get_main_meta_description()
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_descriptions)

        # Fill keywords.
        keywords = parsed_template.find_all(name='meta', attrs={'name': 'keywords', 'content': True})
        if len(keywords) == 1:
            keywords[0]['content'] = config_manager.get_global_keywords()
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_authors)

        # Fill author.
        author = parsed_template.find_all(name='meta', attrs={'name': 'author', 'content': True})
        if len(author) == 1:
            author[0]['content'] = config_manager.get_author()
        else:
            raise UnrecognizedFileException(Strings.exception_parse_multiple_descriptions)

        # Fill script.
        script = parsed_template.find(name='script')
        script.string = config_manager.get_script()

        # Fill global title.
        figure = parsed_template.find(name='header').figure
        figure.figcaption.string = config_manager.get_global_title()
        heading = parsed_template.find(name='h1', attrs={'id': 'heading'})
        heading.string = config_manager.get_global_title()

        # Activate correct menu, generate menu items according to menus.
        menu_container = parsed_template.find(name='nav')
        for menu, instance in self._menus.items():
            new_item = parsed_template.new_tag('a', attrs={'class': 'menu', 'href': instance.get_filename(),
                                               'title': instance.get_page_name()[0]})
            new_item.string = instance.get_page_name()[0]
            if instance.get_filename() == self.get_filename():
                new_item['id'] = 'active'
            menu_container.append(new_item)

        # Fill main page title.
        article = parsed_template.find(name='article', attrs={'class': 'indexPage'})
        article.h2.string = self._page_name

        # Fill text.
        new_black_p = parsed_template.new_tag('p')
        new_black_p.string = config_manager.get_main_page_black_text()

        new_red_p = parsed_template.new_tag('p')
        new_red_p.string = config_manager.get_main_page_red_text()

        article.h2.insert_after(new_red_p)
        article.h2.insert_after(new_black_p)

        # Fill news.
        news = parsed_template.find(name='h3', attrs={'id': 'news'})
        # Sort all articles by date.
        sorted_articles = sorted(self._articles.values(), key=lambda x: x.get_computable_date(), reverse=True)
        for a in sorted_articles:
            print(a)

        print(parsed_template)

        # Fill aside images.
        aside = parsed_template.find(name='aside')
        for img in self._aside_images:
            new_figure = parsed_template.new_tag('figure')
            new_figcaption = parsed_template.new_tag('figcaption', attrs={'class': 'photoCaption'})
            href = img.get_full_filename()
            title = img.get_link_title()[0]
            src = img.get_thumbnail_filename()
            alt = img.get_image_alt()[0]
            text = img.get_caption()[0]
            new_figcaption.string = text
            new_a = parsed_template.new_tag('a', attrs={'href': href, 'target': Strings.blank, 'title': title})
            # Width and height are different from the thumbnail here because the image expands in the page.
            new_img = parsed_template.new_tag('img', attrs={'src': src, 'alt': alt,
                                                            'width': Numbers.aside_thumbnail_width,
                                                            'height': Numbers.aside_thumbnail_height,
                                                            'class': 'imgAside'})
            new_a.append(new_img)
            new_figure.append(new_a)
            new_figure.append(new_figcaption)
            aside.append(new_figure)

        output = str(parsed_template)
        is_valid, errors = Tools.validate(output, 'schema_index.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_bug + '\n' + self.get_filename() + ' \n' + str(errors))

        self._html = output

    # Getters ----------------------------------------------------------------------------------------------------------

    # Setters ----------------------------------------------------------------------------------------------------------
