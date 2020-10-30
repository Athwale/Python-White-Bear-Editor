import os
import re
from typing import List, Dict

import wx
from bs4.element import NavigableString, Tag
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

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
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu


class WhitebearDocumentArticle(WhitebearDocument):
    """
    This class represents an article file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str, menus: Dict[str, WhitebearDocumentMenu], articles,
                 css: WhitebearDocumentCSS):
        """
        Create a new WhitebearDocumentArticle object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        :param menus: A dictionary of WhitebearDocuments representing menus
        :param articles: A dictionary of WhitebearDocuments representing other loaded articles
        :param css: The parsed CSS stylesheet
        """
        # File properties are in base class
        super().__init__(name, path)
        self._date_regex = '^[1-9][0-9]{0,1}[.][ ](' + Strings.cz_months + ')[ ][1-9][0-9][0-9][0-9]$'
        self._menus = menus
        self._articles = articles
        self._css_document = css

        # Article data
        self._menu_section = None
        self._menu_item = None
        self._aside_images = []
        self._main_text_elements = []
        self._links = []
        self._images = set()
        self._videos = set()

        self._date = None
        self._date_error_message: str = ''
        self._main_text = None

        # TODO Store image inside an AsideImage instance
        self._article_image = None

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
        self._parse_main_article_image()
        self._determine_menu_section_and_menu_item()
        self._parse_aside_images()
        self._parse_main_text()
        self.seo_test_self()

    def seo_test_self(self) -> None:
        """
        Perform a SEO test on this document.
        :return: None
        """
        # TODO Run self test on every setter method.
        # TODO backup color in case it is blue
        # Check meta keywords and description
        super(WhitebearDocumentArticle, self).seo_test_self_basic()
        # Check page name length must be at least 3 and must not be default
        # Clear all errors on every new test
        self._date_error_message: str = ''

        if len(self._page_name) < Numbers.article_name_min_length or len(
                self._page_name) > Numbers.article_name_max_length:
            self._page_name_error_message = Strings.seo_error_name_length
            self.set_status_color(Numbers.RED_COLOR)

        if self._page_name == Strings.label_article_title:
            self._page_name_error_message = Strings.seo_error_default_value
            self.set_status_color(Numbers.RED_COLOR)

        # Check date format
        if not re.search(self._date_regex, self._date):
            self._date_error_message = Strings.seo_error_date_format
            self.set_status_color(Numbers.RED_COLOR)
        else:
            day, _, year = self._date.split(' ', 3)
            # Check day range
            if int(day.replace('.', '')) < 1 or int(day.replace('.', '')) > 31:
                self._date_error_message = Strings.seo_error_date_format_day
                self.set_status_color(Numbers.RED_COLOR)

            # Check year range
            if int(year) < Numbers.year_min or int(year) > Numbers.year_max:
                self._date_error_message = Strings.seo_error_date_format_year
                self.set_status_color(Numbers.RED_COLOR)

        # Test main image
        if not self._article_image.seo_test_self():
            self.set_status_color(Numbers.RED_COLOR)

        # Test menu item
        if not self._menu_item.seo_test_self():
            self.set_status_color(Numbers.RED_COLOR)

        # Test aside images
        for aside_image in self._aside_images:
            if not aside_image.seo_test_self():
                self.set_status_color(Numbers.RED_COLOR)

        # Test videos
        for video in self._videos:
            if not video.seo_test_self():
                self.set_status_color(Numbers.RED_COLOR)

        # Test in text images
        for image in self._images:
            if not image.seo_test_self():
                self.set_status_color(Numbers.RED_COLOR)

        # Test links
        for link in self._links:
            if not link.seo_test_self():
                self.set_status_color(Numbers.RED_COLOR)

    def _determine_menu_section_and_menu_item(self) -> None:
        """
        Find out which menu this article belongs in.
        :return: None
        :raises WrongFormatException: If the article is not found in any menu.
        """
        for menu in self._menus.values():
            self._menu_item = menu.find_item_by_file_name(self.get_filename())
            if self._menu_item:
                self._menu_section = menu
                break
        if not self._menu_item:
            raise WrongFormatException(Strings.exception_menu_item_missing + ' for: ' + self.get_filename())

    def _parse_main_text(self) -> None:
        """
        Parse the main text of the article.
        :return: None
        """
        self._main_text_elements.clear()
        self._images.clear()
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
                    self._images.add(image)
                    self._main_text_elements.append(image)
                elif child.next.name == 'iframe':
                    video = self._process_iframe(child)
                    self._videos.add(video)
                    self._main_text_elements.append(video)
            else:
                raise WrongFormatException(Strings.exception_html_syntax_error)

    @staticmethod
    def _process_iframe(div: Tag) -> Video:
        """
        Process a video.
        :param div: The beautiful soup div element containing a video.
        :return: Video instance.
        """
        height = int(div.iframe['height'])
        width = int(div.iframe['width'])
        src = div.iframe['src']
        title = div.iframe['title']
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

        if not os.path.exists(full_original_image_path) or not os.access(full_original_image_path, os.R_OK) \
                or not os.access(full_original_image_path, os.W_OK):
            full_original_image_path = None

        if not os.path.exists(full_thumbnail_path) or not os.access(full_thumbnail_path, os.R_OK) \
                or not os.access(full_thumbnail_path, os.W_OK):
            full_thumbnail_path = None

        return ImageInText(title, alt, full_original_image_path, full_thumbnail_path, div.a['href'], div.img['src'])

    @staticmethod
    def _process_h(h: Tag) -> Heading:
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
        return Heading(Text(text, color=color), size)

    def _process_ul(self, ul: Tag) -> UnorderedList:
        """
        Process an 'ul' tag in the text.
        :param ul: The beautiful soup ul element.
        :return: An UnorderedList instance
        """
        unordered_list = UnorderedList()
        for li in ul.children:
            paragraph = self._process_p(li)
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
            if not self._process_visual_tags(child, paragraph, False):
                if child.name == 'a':
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
            paragraph.add_element(Text(str(parent_element), bold=bold))
        elif parent_element.name == 'span':
            return_value = True
            color = self._css_document.translate_color(parent_element.attrs['class'][0])
            paragraph.add_element(Text(str(parent_element.string), bold=bold, color=color))
        elif parent_element.name == 'br':
            return_value = True
            paragraph.add_element(Break())
        elif parent_element.name == 'strong':
            return_value = True
            # These can also contain colored spans and br, recursively call self
            for child in parent_element.children:
                self._process_visual_tags(child, paragraph, True)
        return return_value

    def _parse_page_name(self) -> None:
        """
        Parse the name of this article and save it into an instance variable.
        :return: None
        """
        article = self._parsed_html.find(name='article', attrs={'class': 'textPage'})
        self._page_name = article.h2.string

    def _parse_date(self) -> None:
        """
        Parse the date stamp of this document and save it into an instance variable.
        :return: None
        """
        self._date = self._parsed_html.find(name='p', attrs={'id': 'date'}).string

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
        errors = []
        try:
            xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path('schema_article.xsd')))
            xml_doc = html.parse(self.get_path())
            self._valid = xmlschema.validate(xml_doc)
        except XMLSyntaxError as e:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + str(e))
        for error in xmlschema.error_log:
            errors.append(error.message)
        return self._valid, errors

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_date(self) -> (str, str):
        """
        Return the article creation date and error to display in gui if there is one.
        :return: Return article creation date and error to display in gui if there is one.
        """
        return self._date, self._date_error_message

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

    def is_modified(self) -> bool:
        """
        Return True if this file or it's images, links or videos were modified in the editor.
        :return: True if this file was modified in the editor.
        """
        # Check links, videos and images
        for list_var in [self._aside_images, self._images, self._links, self._videos]:
            for content in list_var:
                if content.is_modified():
                    self.set_modified(True)
        if self._article_image.is_modified():
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

    def get_other_articles(self) -> Dict:
        """
        Return a dictionary of WhitebearDocuments representing other loaded articles
        :return: A dictionary of WhitebearDocuments representing other loaded articles
        """
        return self._articles

    def find_link(self, link_id: str) -> Link:
        """
        Find the link instance identified by the text and url parameters.
        :param link_id: Unique identifier of a Link
        :return: a Link instance
        """
        for link in self._links:
            if link.get_id() == link_id:
                return link

    def add_link(self, link: Link) -> None:
        """
        Append a new link into the link list.
        :param link: The new link
        :return: None
        """
        # TODO use the link list when regenerating elements list
        self._links.append(link)
        self.set_modified(True)

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_date(self, date: str) -> None:
        """
        Set the new article date.
        Change modified attribute to True.
        :param date: New article creation date.
        :return: None
        """
        self._date = date
        self.set_modified(True)
