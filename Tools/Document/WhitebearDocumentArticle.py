import datetime
import os
import re
import time
from typing import List, Dict

import wx
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Exceptions.WrongFormatException import WrongFormatException
from Resources.Fetch import Fetch
from Tools.Document.ArticleElements.Heading import Heading
from Tools.Document.ArticleElements.ImageInText import ImageInText
from Tools.Document.ArticleElements.Link import Link
from Tools.Document.ArticleElements.Paragraph import Paragraph
from Tools.Document.ArticleElements.Text import Text, Break
from Tools.Document.ArticleElements.UnorderedList import UnorderedList
from Tools.Document.ArticleElements.Video import Video
from Tools.Document.AsideImage import AsideImage
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class WhitebearDocumentArticle(WhitebearDocument):
    """
    This class represents an article file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, path: str, menus: Dict[str, WhitebearDocumentMenu], articles,
                 css: WhitebearDocumentCSS):
        """
        Create a new WhitebearDocumentArticle object.
        :param path: Full path on disk to the file
        :param menus: A dictionary of WhitebearDocuments representing menus
        :param articles: A dictionary of WhitebearDocuments representing other loaded articles
        :param css: The parsed CSS stylesheet
        """
        # File properties are in base class
        super().__init__(path)
        self._date_regex = '^[1-9][0-9]{0,1}[.][ ](' + Strings.cz_months + ')[ ][1-9][0-9][0-9][0-9]$'
        self._menus = menus
        self._articles = articles
        self._css_document = css
        self._index_document = None
        self._enabled = False

        # Article data
        self._menu_section = None
        self._menu_item = None
        self._aside_images = []
        self._main_text_elements = []
        self._links = []
        self._text_images = []
        self._videos = []

        self._date = ''
        self._date_error_message: str = ''
        self._spelling_error_message: str = ''
        self._main_text = None
        self._plain_text: str = ''

        self._article_image = None
        self._html = ''

    def parse_self(self) -> None:
        """
        Parse this document and fill internal variables with content.
        Call validate_self before parsing.
        :return: None
        :raises WrongFormatException: if there is a problem with parsing the document.
        """
        super(WhitebearDocumentArticle, self).parse_self()
        self._parse_page_name()
        self._parse_date()
        self.determine_menu_section_and_menu_item()
        self._parse_main_article_image()
        self._parse_aside_images()
        self._parse_main_text()
        self._parse_enabled_attribute()
        self.test_self(self._config_manager.get_online_test())

    def seo_test_date(self, date: str) -> (bool, str, wx.Colour):
        """
        SEO test date and return False, error string and new status color if incorrect.
        :param date: The name to check
        :return: Return False, error string and new status color if incorrect.
        """
        date_error_message = Strings.status_ok
        result = True
        color = Numbers.GREEN_COLOR
        if not re.search(self._date_regex, date):
            date_error_message = Strings.seo_error_date_format
            result = False
        else:
            day, _, year = date.split(' ', 3)
            # Check day range
            if int(day.replace('.', '')) < 1 or int(day.replace('.', '')) > 31:
                date_error_message = Strings.seo_error_date_format_day
                result = False

            # Check year range
            if int(year) < Numbers.year_min or int(year) > Numbers.year_max:
                date_error_message = Strings.seo_error_date_format_year
                result = False

        if not result:
            color = Numbers.RED_COLOR
        return result, date_error_message, color

    def test_self(self, online: bool) -> bool:
        """
        Perform a SEO test on this document and set it's status color.
        # TODO new colors:
        # white - ok, saved, uploaded
        # blue - ok, not uploaded
        # red - error, turns to blue when fixed.
        # bold - modified and not saved.
        :param online: Do online test of urls.
        :return: True if seo test passed.
        """
        # Check meta keywords and description. Resets color to white in the beginning. Result color might be red.
        basic_result: bool = super(WhitebearDocumentArticle, self).test_self_basic()
        if basic_result and self.is_modified():
            self.set_status_color(Numbers.BLUE_COLOR)
        if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
            print('basic ', str(self.get_status_color()), self.get_page_name())
        # TODO What about setting modified from somewhere else?
        # TODO Redraw colors of all uploaded once done.
        # TODO implement bold
        # TODO test upload turning documents white
        if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
            print('modified: ', self._modified, self.get_status_color())
            print('saved: ', self.is_saved())
        # Clear all errors on every new test
        self._date_error_message: str = ''
        self._spelling_error_message: str = ''

        # Check page name length must be at least 3 and must not be default.
        name_result, message, color = self.seo_test_name(self._page_name)
        # Message may contain OK if seo passed.
        self._page_name_error_message = message
        if not name_result:
            if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                print('name')
            self.set_status_color(color)

        # Check date format
        date_result, message, color = self.seo_test_date(self._date)
        self._date_error_message = message
        if not date_result:
            if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                print('date')
            self.set_status_color(color)

        # Test main image
        if not self._article_image.test_self():
            if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                print('main img')
            self.set_status_color(Numbers.RED_COLOR)

        # Test menu item
        if not self._menu_item.test_self():
            if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                print('menu')
            self.set_status_color(Numbers.RED_COLOR)

        # Test aside images
        for aside_image in self._aside_images:
            if not aside_image.test_self():
                if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                    print('aside')
                self.set_status_color(Numbers.RED_COLOR)

        # Test videos
        for video in self._videos:
            if not video.test_self(online):
                if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                    print('video')
                self.set_status_color(Numbers.RED_COLOR)

        # Test in text images
        for image in self._text_images:
            if not image.test_self():
                if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                    print('imgs')
                self.set_status_color(Numbers.RED_COLOR)

        # Test links
        for link in self._links:
            if not link.test_self(online):
                if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                    print('links')
                self.set_status_color(Numbers.RED_COLOR)

        if not self._spell_check(self._plain_text):
            self._spelling_error_message = Strings.spelling_error
            if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
                print('spell')
            self.set_status_color(Numbers.RED_COLOR)

        if not self._enabled:
            self.set_status_color(Numbers.RED_COLOR)

        if 'Projekt krátkého wiki filmu' in self.get_page_name()[0]:
            print('end ', str(self.get_status_color()), self.get_page_name(), '\n')

        if self.get_status_color() == Numbers.RED_COLOR:
            return False
        return True

    def determine_menu_section_and_menu_item(self) -> None:
        """
        Find out which menu this article belongs in.
        :return: None
        :raises WrongFormatException: If the article is not found in any menu.
        """
        for menu in self._menus.values():
            self._menu_item = menu.find_item_by_file_name(self.get_filename())
            if self._menu_item:
                self._menu_item.set_article(self)
                # We do not want the items to start as modified when the document is loaded, but set makes them modified
                self._menu_item.set_modified(False)
                self._menu_section = menu
                break
        if not self._menu_item:
            raise WrongFormatException(Strings.exception_menu_item_missing + ' for: ' + self.get_filename())

    def _parse_enabled_attribute(self) -> None:
        """
        Determine whether the publication of this article is enabled or whether this article is not finished.
        :return: None
        """
        # Find a section tag with both classes, if such is present, the article is disabled.
        # Returns true when the disabled class is present, so it has to be negated.
        self._enabled = not (bool(self._parsed_html.select('section.mainText.disabled')))

    def _parse_main_text(self) -> None:
        """
        Parse the main text of the article.
        :return: None
        """
        self._main_text_elements.clear()
        self._text_images.clear()
        self._links.clear()
        self._videos.clear()
        text_section = self._parsed_html.find(name='section', attrs={'class': 'mainText'})
        child: Tag
        for child in text_section.children:
            # These can be p, ul, h3, h4, div
            if child.name == 'p':
                # These can be text, span, strong, a, br
                self._main_text_elements.append(self._process_p(child))
            elif child.name == 'ul':
                self._main_text_elements.append(self._process_ul(child))
            elif child.name == 'h3' or child.name == 'h4':
                self._main_text_elements.append(self._process_h(child))
            elif child.name == 'div':
                if child.next.name == 'a':
                    image = self._process_img(child)
                    self._text_images.append(image)
                    self._main_text_elements.append(image)
                elif child.next.name == 'iframe':
                    video = self._process_iframe(child)
                    self._videos.append(video)
                    self._main_text_elements.append(video)
            else:
                raise WrongFormatException(Strings.exception_html_syntax_error)

    def _process_iframe(self, div: Tag) -> Video:
        """
        Process a video.
        :param div: The beautiful soup div element containing a video.
        :return: Video instance.
        """
        height = int(div.iframe['height'])
        width = int(div.iframe['width'])
        src = div.iframe['src']
        title = div.iframe['title']
        self._plain_text += '\n'

        return Video(title, width, height, src)

    def _process_img(self, div: Tag):
        """
        Process an in text image.
        :param div: The beautiful soup div element containing an in text image.
        :return: ImageInText instance.
        """
        full_original_image_path = os.path.join(self._working_directory, div.a['href'])
        title = div.a['title']
        alt = div.img['alt']
        full_thumbnail_path = os.path.join(self._working_directory, div.img['src'])
        self._plain_text += '\n'

        if not os.path.exists(full_original_image_path) or not os.access(full_original_image_path, os.R_OK) \
                or not os.access(full_original_image_path, os.W_OK):
            full_original_image_path = None

        if not os.path.exists(full_thumbnail_path) or not os.access(full_thumbnail_path, os.R_OK) \
                or not os.access(full_thumbnail_path, os.W_OK):
            full_thumbnail_path = None

        return ImageInText(title, alt, full_original_image_path, full_thumbnail_path, div.a['href'], div.img['src'])

    def _process_h(self, h: Tag) -> Heading:
        """
        Process a 'h' tag in the text.
        :param h: The beautiful soup h element.
        :return: An Heading instance
        """
        # The h element can have a color class.
        size = 0
        text = str(h.string)
        color = 'black'
        if h.name == 'h3':
            size = Heading.SIZE_H3
        elif h.name == 'h4':
            size = Heading.SIZE_H4
        if size == 0:
            raise WrongFormatException(Strings.exception_html_syntax_error)
        if h.has_attr('class'):
            color = h.attrs['class'][0]
        self._plain_text += text + '\n'
        return Heading(Text(text, color=color), size)

    def _process_ul(self, ul: Tag) -> UnorderedList:
        """
        Process an 'ul' tag in the text.
        :param ul: The beautiful soup ul element.
        :return: An UnorderedList instance
        """
        unordered_list = UnorderedList()
        for li in ul.children:
            li: Tag
            paragraph = self._process_p(li)
            self._plain_text += '\n'
            unordered_list.append_paragraph(paragraph)
        return unordered_list

    def _process_p(self, p: Tag) -> Paragraph:
        """
        Process a 'p' tag in the text.
        :param p: The beautiful soup p element.
        :return: a Paragraph instance
        """
        paragraph = Paragraph()
        for child in p.children:
            # These can be text, span, strong, a, br
            child: Tag
            if not self._process_visual_tags(child, paragraph, False):
                if child.name == 'a':
                    self._plain_text += child.string
                    link = Link(str(child.string), child.attrs['href'], child.attrs['title'], self._articles,
                                self._working_directory)
                    paragraph.add_element(link)
                    self._links.append(link)
                else:
                    raise WrongFormatException(Strings.exception_html_syntax_error)
        return paragraph

    def _process_visual_tags(self, parent_element: Tag, paragraph: Paragraph, bold: bool) -> bool:
        """
        Process span, br and strong
        :param parent_element: the element containing the tags to process.
        :param paragraph: The Paragraph instance to put the processed elements in.
        :param bold: If True, apply bold True to any Text.
        :return: True if something was processed
        """
        return_value = False
        if isinstance(parent_element, NavigableString):
            return_value = True
            self._plain_text += str(parent_element)
            paragraph.add_element(Text(str(parent_element), bold=bold))
        elif parent_element.name == 'span':
            # These can contain br
            return_value = True
            color = parent_element.attrs['class'][0]
            for child in parent_element.children:
                if child.name == 'br':
                    self._plain_text += '\n'
                    paragraph.add_element(Break())
                else:
                    self._plain_text += child.string
                    paragraph.add_element(Text(str(child.string), bold=bold, color=color))
        elif parent_element.name == 'br':
            return_value = True
            self._plain_text += '\n'
            paragraph.add_element(Break())
        elif parent_element.name == 'strong':
            return_value = True
            # These can also contain colored spans and br, recursively call self
            for child in parent_element.children:
                child: Tag
                self._process_visual_tags(child, paragraph, True)
        return return_value

    def _parse_page_name(self) -> None:
        """
        Parse the name of this article and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'textPage'})
        name = str(article.h2.string)
        self._page_name = name if name else ''

    def _parse_date(self) -> None:
        """
        Parse the date stamp of this document and save it into an instance variable.
        :return: None
        """
        self._date = str(self._parsed_html.find(name='p', attrs={'id': 'date'}).string)

    def _parse_main_article_image(self) -> None:
        """
        Parse the main article image into an AsideImage instance
        :return: None
        """
        main_image_figure = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'})
        self._article_image = self._prepare_aside_image(main_image_figure)

    def _parse_aside_images(self) -> None:
        """
        Parse aside images into a list of special container classes.
        :return: None
        """
        self._aside_images.clear()
        aside = self._parsed_html.find(name='aside')
        figures = aside.find_all(name='figure')
        if figures:
            for figure in figures:
                self._aside_images.append(self._prepare_aside_image(figure))

    def _prepare_aside_image(self, figure: Tag) -> AsideImage:
        """
        Parse and prepare an AsideImage instance from html figure.
        :param figure: The html whitebear figure element.
        :return: A new instance of AsideImage
        """
        full_original_image_path = os.path.join(self._working_directory, figure.a['href'])
        title = figure.a['title']
        alt = figure.img['alt']
        full_thumbnail_path = os.path.join(self._working_directory, figure.img['src'])
        string_content = figure.figcaption.strings
        figcaption = ''.join(string_content)

        if not os.path.exists(full_original_image_path) or not os.access(full_original_image_path, os.R_OK) \
                or not os.access(full_original_image_path, os.W_OK):
            full_original_image_path = None

        if not os.path.exists(full_thumbnail_path) or not os.access(full_thumbnail_path, os.R_OK) \
                or not os.access(full_thumbnail_path, os.W_OK):
            full_thumbnail_path = None

        return AsideImage(figcaption, title, alt, full_original_image_path, full_thumbnail_path, figure.a['href'],
                          figure.img['src'])

    def validate_self(self) -> (bool, List[str]):
        """
        Validate this document against the article xml schema.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails
        """
        with open(self.get_path(), 'r') as file:
            html_string = file.read()
        self._valid, errors = Tools.validate(html_string, 'schema_article.xsd')
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
        with open(Fetch.get_resource_path('article_template.html'), 'r') as template:
            template_string = template.read()
        is_valid, errors = Tools.validate(template_string, 'schema_article_template.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + 'article_template.html ' +
                                            str(errors))

        parsed_template = BeautifulSoup(template_string, 'html5lib')

        # Fill title.
        title: Tag = parsed_template.find(name='title')
        title.string = self._page_name + ' - ' + self._menu_section.get_section_name() + ' | ' + Strings.page_name

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
            if instance.get_filename() == self._menu_section.get_filename():
                new_item['id'] = 'active'
            menu_container.append(new_item)

        # Fill main page title.
        article = parsed_template.find(name='article', attrs={'class': 'textPage'})
        article.h2.string = self._page_name

        # Fill date.
        parsed_template.find(name='p', attrs={'id': 'date'}).string = self._date

        # Fill main image.
        main_image_figure = parsed_template.find(name='figure', attrs={'id': 'articleImg'})
        main_image_figure.a['href'] = self.get_article_image().get_full_filename()
        main_image_figure.a['title'] = self.get_article_image().get_link_title()[0]
        main_image_figure.img['src'] = self.get_article_image().get_thumbnail_filename()
        main_image_figure.img['alt'] = self.get_article_image().get_image_alt()[0]
        main_image_figure.figcaption.string = self.get_article_image().get_caption()[0]

        # Fill main text.
        text_section = parsed_template.find(name='section', attrs='mainText')
        if not self._enabled:
            # Save the disabled state into the html, once the article is enabled, this special class will be removed.
            text_section['class'] = 'mainText disabled'
        for element in self.get_main_text_elements():
            if isinstance(element, Heading):
                size = 'h3' if element.get_size() == Heading.SIZE_H3 else 'h4'
                text = element.get_text().get_text()
                color = element.get_text().get_color()
                new_h = parsed_template.new_tag(size)
                new_h.string = text
                if color != Strings.color_black:
                    # Black text is default, so ignore it.
                    new_h['class'] = color
                text_section.append(new_h)
            elif isinstance(element, ImageInText):
                new_div = parsed_template.new_tag('div', attrs={'class': 'center'})
                href = element.get_full_filename()
                title = element.get_link_title()[0]
                src = element.get_thumbnail_filename()
                alt = element.get_image_alt()[0]
                width = element.get_thumbnail_size()[0]
                height = element.get_thumbnail_size()[1]
                new_a = parsed_template.new_tag('a', attrs={'href': href, 'target': Strings.blank, 'title': title})
                new_img = parsed_template.new_tag('img', attrs={'src': src, 'alt': alt, 'width': width,
                                                                'height': height})
                new_a.append(new_img)
                new_div.append(new_a)
                text_section.append(new_div)
            elif isinstance(element, Video):
                new_div = parsed_template.new_tag('div', attrs={'class': 'center'})
                title = element.get_title()[0]
                width = element.get_size()[0]
                height = element.get_size()[1]
                src = element.get_url()[0]
                new_iframe = parsed_template.new_tag('iframe', attrs={'title': title, 'height': height,
                                                                      'width': width, 'src': src,
                                                                      'allowfullscreen': None})
                new_div.append(new_iframe)
                text_section.append(new_div)
            elif isinstance(element, Paragraph):
                new_p = parsed_template.new_tag('p')
                new_p = self._convert_text_contents(new_p, element, parsed_template)
                text_section.append(new_p)
            elif isinstance(element, UnorderedList):
                new_ul = parsed_template.new_tag('ul')
                for par in element.get_paragraphs():
                    new_li = parsed_template.new_tag('li')
                    self._convert_text_contents(new_li, par, parsed_template)
                    new_ul.append(new_li)
                text_section.append(new_ul)

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
        is_valid, errors = Tools.validate(output, 'schema_article.xsd')
        if not is_valid:
            raise UnrecognizedFileException(Strings.exception_bug + '\n' + self.get_filename() + ' \n' + str(errors))

        self._html = output
        # Save the fact that this file is changed into the list of file that we need to upload. This survives editor
        # exit and can be restored on start. This list is cleared when a file is uploaded.
        self._config_manager.store_not_uploaded(self.get_filename())

    @staticmethod
    def _convert_text_contents(container: Tag, par: Paragraph, soup: BeautifulSoup) -> Tag:
        """
        Converts a Paragraph instance into the contents of either <p> or <li>.
        :param container: The containing parent either <p> or <li>
        :param par: The Paragraph instance to convert.
        :param soup: The parsed template for creating new tags.
        :return: The filled container.
        """
        new_strong = None
        new_span = None
        for element in par.get_elements():
            # List of instances of Text, Break and Link.
            if isinstance(element, Text):
                bold = element.is_bold()
                color = element.get_color()
                text = element.get_text()
                if bold:
                    new_strong = soup.new_tag('strong')
                if color != Strings.color_black:
                    new_span = soup.new_tag('span', attrs={'class': color})
                # Four possibilities: Bold, normal, colored, bold colored.
                if not bold and color == Strings.color_black:
                    # Ordinary text content.
                    container.append(text)
                if bold and color == Strings.color_black:
                    # Normal black bold text.
                    new_strong.string = text
                    container.append(new_strong)
                if not bold and color != Strings.color_black:
                    # Colored thin text.
                    new_span.string = text
                    container.append(new_span)
                if bold and color != Strings.color_black:
                    # Colored bold text.
                    new_span.string = text
                    new_strong.append(new_span)
                    container.append(new_strong)
            elif isinstance(element, Link):
                href = element.get_url()[0]
                title = element.get_title()[0]
                text = element.get_text()[0]
                new_a = soup.new_tag('a', attrs={'href': href, 'title': title, 'target': Strings.blank})
                new_a.string = text
                container.append(new_a)
            elif isinstance(element, Break):
                container.append(soup.new_tag('br'))
        return container

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_plain_text(self) -> str:
        """
        Get the text of the page excluding images and videos.
        :return: The text of the page excluding images and videos.
        """
        return self._plain_text

    def get_html_to_save(self) -> str:
        """
        Returns the last converted string HTML code of this page. Run convert_to_html() before calling this method.
        :return: String HTML of the article or none if the document was not converted yet.
        """
        return self._html

    def get_date(self) -> (str, str):
        """
        Return the article creation date and error to display in gui if there is one.
        :return: Return article creation date and error to display in gui if there is one.
        """
        return self._date, self._date_error_message

    def get_computable_date(self) -> float:
        """
        Convert article date into a flot timestamp.
        :return: Date as float timestamp.
        """
        month_dict = {k: v for k, v in zip(Strings.cz_months.split('|'), range(1, 13))}
        day = self._date.split('.', 1)[0]
        try:
            month = month_dict[self._date.split(' ', 2)[1]]
        except KeyError as _:
            # Return a value in case the date is wrong, the user will have to correct it when uploading anyway.
            return 1
        year = self._date.split(' ', 2)[2]
        return time.mktime(datetime.datetime.
                           strptime(str(day) + '/' + str(month) + '/' + str(year), "%d/%m/%Y").timetuple())

    def get_article_image(self) -> AsideImage:
        """
        Return the article image AsideImage instance.
        :return: Return the article AsideImage instance.
        """
        return self._article_image

    def get_menu_item(self) -> MenuItem:
        """
        Return the menu item associated with this article.
        :return: The menu item associated with this article.
        """
        return self._menu_item

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        :return: Return the status color of this document. White if ok, Red if SEO check failed, Blue if modified.
        """
        return self._status_color

    def is_enabled(self) -> bool:
        """
        Returns True if publication of this article is enabled.
        :return: True if publication of this article is enabled.
        """
        return self._enabled

    def is_modified(self) -> bool:
        """
        Return True if this file or it's images, links or videos were modified in the editor.
        :return: True if this file was modified in the editor.
        """
        # Check links, videos and images
        for list_var in (self._aside_images, self._text_images, self._links, self._videos):
            for content in list_var:
                if content.is_modified():
                    self.set_modified(True)
        if self._article_image.is_modified():
            self.set_modified(True)
        if self._menu_item.is_modified():
            self.set_modified(True)
        return self._modified

    def get_menu_section(self) -> WhitebearDocumentMenu:
        """
        Return to which menu section this article belongs.
        :return: Return to which menu section this article belongs.
        """
        return self._menu_section

    def get_aside_images(self) -> List[AsideImage]:
        """
        Return the aside images of this article.
        :return: the aside images of this article
        """
        return self._aside_images

    def get_main_text_elements(self) -> List:
        """
        Return a list of main text elements which are Heading, ImageInText, Paragraph, Video, UnorderedList
        :return: a list of main text elements which are Heading, ImageInText, Paragraph, Video, UnorderedList
        """
        return self._main_text_elements

    def get_links(self) -> List[Link]:
        """
        Return a list of all links which are in current text elements.
        :return: A list of all links which are in current text elements
        """
        return self._links

    def get_text_images(self) -> List[ImageInText]:
        """
        Return a list of all images in text which are in current text elements.
        :return: A list of all images in text which are in current text elements
        """
        return self._text_images

    def get_other_articles(self) -> Dict:
        """
        Return a dictionary of WhitebearDocuments representing other loaded articles
        :return: A dictionary of WhitebearDocuments representing other loaded articles
        """
        return self._articles

    def get_other_menus(self) -> Dict[str, WhitebearDocumentMenu]:
        """
        Returns other parsed menus.
        :return: Returns other parsed menus.
        """
        return self._menus

    def get_css_document(self) -> WhitebearDocumentCSS:
        """
        Return the css document instance.
        :return: The WhitebearDocumentCSS instance.
        """
        return self._css_document

    def get_index_document(self) -> WhitebearDocumentIndex:
        """
        Return the index document instance.
        :return: The WhitebearDocumentIndex instance.
        """
        return self._index_document

    def find_link(self, link_id: str) -> Link:
        """
        Find the link instance identified by the id.
        :param link_id: Unique identifier of a Link
        :return: a Link instance
        """
        for link in self._links:
            if link.get_id() == link_id:
                return link

    def find_in_text_image(self, image_id: int) -> ImageInText:
        """
        Find and return an ImageInText instance based on the image's thumbnail disk path.
        :param image_id: ID of the image.
        :return: A ImageInText instance.
        """
        for img in self._text_images:
            img: ImageInText
            if img.get_id() == image_id:
                return img

    def find_video(self, video_id: int) -> Video:
        """
        Find and return a Video instance based on the url of the video.
        :param video_id: ID of the video.
        :return: A Video instance.
        """
        for video in self._videos:
            video: Video
            if video.get_id() == video_id:
                return video

    def add_link(self, link: Link) -> None:
        """
        Append a new link into the link list.
        :param link: The new link
        :return: None
        """
        self._links.append(link)
        self.set_modified(True)

    def remove_link(self, link_id: str) -> None:
        """
        Remove a Link from the list of links based on id,
        :param link_id: Unique identifier of a Link
        :return: None
        """
        for link in self._links:
            if link.get_id() == link_id:
                self._links.remove(link)
        self.set_modified(True)

    def add_image(self, image: ImageInText) -> None:
        """
        Add a new in text image into the document.
        :param image: The new image.
        :return: None
        """
        self._text_images.append(image)
        self.set_modified(True)

    def add_video(self, video: Video) -> None:
        """
        Add a new video into the document.
        :param video: The new video.
        :return: None
        """
        self._videos.append(video)
        self.set_modified(True)

    def add_aside_image(self, image: ImageInText) -> None:
        """
        Add a new in text image into the document.
        :param image: The new image.
        :return: None
        """
        self._aside_images.append(image)
        self.set_modified(True)

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_plain_text(self, text: str) -> None:
        """
        Set new plain text. This does not change modified state because this is just used for spellcheck test.
        :param text: New plain text.
        :return: None
        """
        self._plain_text = text

    def set_enabled(self, enabled: bool) -> None:
        """
        Sets the publication enabled attribute.
        :param enabled: True if article publication is enabled.
        :return: None
        """
        self._enabled = enabled
        self.set_modified(True)

    def set_index_document(self, index: WhitebearDocumentIndex) -> None:
        """
        Set the index document instance.
        :param index: The index document.
        :return: None
        """
        self._index_document = index

    def set_date(self, date: str) -> None:
        """
        Set the new article date.
        Change modified attribute to True.
        :param date: New article creation date.
        :return: None
        """
        if date != self._date:
            self._date = date
            self.set_modified(True)

    def set_article_image(self, img: AsideImage) -> None:
        """
        Set the new article image.
        Change modified attribute to True.
        :param img: New image.
        :return: None
        """
        if img != self._article_image:
            self._article_image = img
            self.set_modified(True)

    def set_modified(self, modified: bool) -> None:
        """
        Set modification status for the document. If False then all parts of the document are set to not be modified.
        Clear last known converted html since something has changed.
        :param modified: The new state.
        :return: None
        """
        super(WhitebearDocumentArticle, self).set_modified(modified)
        self.clear_converted_html()
        if modified:
            self.set_saved(False)
        if not modified:
            for list_var in (self._aside_images, self._text_images, self._links, self._videos):
                for content in list_var:
                    content.set_modified(False)
            self._article_image.set_modified(False)
            self._menu_item.set_modified(False)

    def set_text_elements(self, elements: List) -> None:
        """
        Set the new article text elements list.
        Change modified attribute to True.
        :param elements: New article elements list.
        :return: None
        """
        if elements != self._main_text_elements:
            # Refill internal lists of text elements with what is actually used in the document and throw away the rest.
            self._links.clear()
            self._text_images.clear()
            self._videos.clear()
            for element in elements:
                if isinstance(element, Video):
                    self._videos.append(element)
                elif isinstance(element, ImageInText):
                    self._text_images.append(element)
                elif isinstance(element, Paragraph):
                    self._links.extend(element.get_links())
                elif isinstance(element, UnorderedList):
                    for paragraph in element.get_paragraphs():
                        self._links.extend(paragraph.get_links())
            self._main_text_elements = elements
            self.set_modified(True)
