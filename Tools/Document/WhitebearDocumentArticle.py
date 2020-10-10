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
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu


class WhitebearDocumentArticle(WhitebearDocument):
    """
    This class represents an article file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    def __init__(self, name: str, path: str, menus: Dict[str, WhitebearDocumentMenu], articles):
        """
        Create a new WhitebearDocumentArticle object.
        :param name: Name of the file.
        :param path: Full path on disk to the file
        :param menus: A dictionary of WhitebearDocuments representing menus
        :param articles: A dictionary of WhitebearDocuments representing other loaded articles
        """
        # File properties are in base class
        super().__init__(name, path)
        self._date_regex = '^[1-9][0-9]{0,1}[.][ ](' + Strings.cz_months + ')[ ][1-9][0-9][0-9][0-9]$'
        self._menus = menus
        self._articles = articles

        # Article data
        self._menu_section = None
        self._menu_item = None
        self._aside_images = []
        self._main_text_elements = []
        self._links = []
        self._images = []
        self._videos = []

        self._date = None
        self._date_error_message: str = ''
        self._article_full_image_path = None
        self._article_thumbnail_image_path = None
        self._article_image_caption = ''
        self._caption_error_message: str = ''
        self._article_image_link_title = None
        self._link_title_error_message: str = ''
        self._article_image_alt = None
        self._image_alt_error_message: str = ''
        self._article_image = None
        self._main_text = None

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
        self._parse_article_image_path()
        self._parse_article_image_caption()
        self._parse_article_image_link_title()
        self._parse_article_image_alt()
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
        # Check meta keywords and description
        super(WhitebearDocumentArticle, self).seo_test_self_basic()
        # Check page name length must be at least 3 and must not be default
        # Clear all errors on every new test
        self._date_error_message: str = ''
        self._caption_error_message: str = ''
        self._link_title_error_message: str = ''
        self._image_alt_error_message: str = ''

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

        # Check article image disk path, original image may have whatever size
        if not self._article_full_image_path:
            self._article_image = wx.Image(Fetch.get_resource_path('main_image_missing.png'), wx.BITMAP_TYPE_PNG)
            self.set_status_color(Numbers.RED_COLOR)
        else:
            # Check article image thumbnail disk path
            if not self._article_thumbnail_image_path:
                self._article_image = wx.Image(Fetch.get_resource_path('main_image_thumbnail_missing.png'),
                                               wx.BITMAP_TYPE_PNG)
                self.set_status_color(Numbers.RED_COLOR)
            else:
                image = wx.Image(Fetch.get_resource_path(self._article_thumbnail_image_path), wx.BITMAP_TYPE_ANY)
                if image.GetSize() == (Numbers.main_image_width, Numbers.main_image_height):
                    self._article_image = image
                else:
                    self._article_image = wx.Image(Fetch.get_resource_path('main_image_thumbnail_wrong.png'),
                                                   wx.BITMAP_TYPE_ANY)
                    self.set_status_color(Numbers.RED_COLOR)

        # Check article image caption
        if len(self._article_image_caption) < Numbers.article_image_caption_min or len(
                self._article_image_caption) > Numbers.article_image_caption_max:
            self._caption_error_message = Strings.seo_error_image_caption_length
            self.set_status_color(Numbers.RED_COLOR)

        if self._article_image_caption == Strings.label_article_image_caption:
            self._image_alt_error_message = Strings.seo_error_default_value
            self.set_status_color(Numbers.RED_COLOR)

        # Check article image link title
        if len(self._article_image_link_title) < Numbers.article_image_title_min or len(
                self._article_image_link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            self.set_status_color(Numbers.RED_COLOR)

        if self._article_image_link_title == Strings.label_article_image_link_title:
            self._link_title_error_message = Strings.seo_error_default_value
            self.set_status_color(Numbers.RED_COLOR)

        # Check article image alt
        if len(self._article_image_alt) < Numbers.article_image_alt_min or len(
                self._article_image_alt) > Numbers.article_image_alt_max:
            self._image_alt_error_message = Strings.seo_error_image_alt_length
            self.set_status_color(Numbers.RED_COLOR)

        if self._article_image_alt == Strings.label_article_image_alt:
            self._image_alt_error_message = Strings.seo_error_default_value
            self.set_status_color(Numbers.RED_COLOR)

        # Test menu item
        if not self._menu_item.seo_test_self():
            self.set_status_color(Numbers.RED_COLOR)

        # Test aside images
        for aside_image in self._aside_images:
            if not aside_image.seo_test_self():
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
        text_section = self._parsed_html.find(name='section', attrs={'class': 'mainText'})
        # TODO run seo check on link, video and in text image and do something with any errors.
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
                    self._images.append(image)
                    self._main_text_elements.append(image)
                elif child.next.name == 'iframe':
                    video = self._process_iframe(child)
                    self._videos.append(video)
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
        height = div.iframe['height']
        width = div.iframe['width']
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
            if not self._process_visual_tags(child, paragraph):
                if child.name == 'a':
                    link = Link(str(child.string), child.attrs['href'], child.attrs['title'], self._articles)
                    paragraph.add_element(link)
                    self._links.append(link)
                else:
                    raise WrongFormatException(Strings.exception_html_syntax_error)
        return paragraph

    def _process_visual_tags(self, parent_element: Tag, paragraph: Paragraph) -> bool:
        """
        Process span, br and strong
        :param parent_element: the element containing the tags to process.
        :param paragraph: The Paragraph instance to put the processed elements in.
        :return: True if something was processed
        """
        return_value = False
        if isinstance(parent_element, NavigableString):
            return_value = True
            paragraph.add_element(Text(str(parent_element)))
        elif parent_element.name == 'span':
            return_value = True
            paragraph.add_element(Text(str(parent_element.string), color=parent_element.attrs['class'][0]))
        elif parent_element.name == 'br':
            return_value = True
            paragraph.add_element(Break())
        elif parent_element.name == 'strong':
            return_value = True
            # These can also contain colored spans and br, recursively call self
            for child in parent_element.children:
                self._process_visual_tags(child, paragraph)
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

    def _parse_article_image_path(self) -> None:
        """
        Parse the absolute path to the main article image and save it into an instance variable.
        If the image is not accessible on disk, the variable is set to None.
        :return: None
        """
        main_image_figure = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'})
        self._article_full_image_path = os.path.join(self._working_directory, main_image_figure.a['href'])
        self._article_thumbnail_image_path = os.path.join(self._working_directory, main_image_figure.img['src'])
        if not os.path.exists(self._article_full_image_path) or \
                not os.access(self._article_full_image_path, os.R_OK) or \
                not os.access(self._article_full_image_path, os.W_OK):
            self._article_full_image_path = None

        if not os.path.exists(self._article_thumbnail_image_path) or \
                not os.access(self._article_thumbnail_image_path, os.R_OK) or \
                not os.access(self._article_thumbnail_image_path, os.W_OK):
            self._article_thumbnail_image_path = None

    def _parse_article_image_caption(self) -> None:
        """
        Parse the main article image caption text and save it into an instance variable.
        :return: None
        """
        main_image_figure = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'})
        # The figcaption tag is allowed to contain <br> which we have to skip
        string_content = main_image_figure.figcaption.strings
        self._article_image_caption = ''.join(string_content)

    def _parse_article_image_link_title(self) -> None:
        """
        Parse the main article image link title text and save it into an instance variable.
        :return: None
        """
        self._article_image_link_title = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'}).a['title']

    def _parse_article_image_alt(self) -> None:
        """
        Parse the main article image alt description text and save it into an instance variable.
        :return: None
        """
        self._article_image_alt = self._parsed_html.find(name='figure', attrs={'id': 'articleImg'}).img['alt']

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
                full_original_image_path = os.path.join(self._working_directory, figure.a['href'])
                title = figure.a['title']
                alt = figure.img['alt']
                full_thumbnail_path = os.path.join(self._working_directory, figure.img['src'])
                figcaption = figure.figcaption.string

                if not os.path.exists(full_original_image_path) or not os.access(full_original_image_path, os.R_OK) \
                        or not os.access(full_original_image_path, os.W_OK):
                    full_original_image_path = None

                if not os.path.exists(full_thumbnail_path) or not os.access(full_thumbnail_path, os.R_OK) \
                        or not os.access(full_thumbnail_path, os.W_OK):
                    full_thumbnail_path = None

                self._aside_images.append(
                    AsideImage(figcaption, title, alt, full_original_image_path, full_thumbnail_path, figure.a['href'],
                               figure.img['src']))

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

    def get_article_image_path(self) -> str:
        """
        Return the path to the article image full version.
        :return: Return the path to the article image full version.
        """
        return self._article_full_image_path

    def get_article_image(self) -> wx.Image:
        """
        Return the article image wx image instance.
        :return: Return the article image wx image instance.
        """
        return self._article_image

    def get_article_image_caption(self) -> (str, str):
        """
        Return the caption of the main article image and error to display in gui if there is one.
        :return: Return the caption of the main article image and error to display in gui if there is one.
        """
        return self._article_image_caption, self._caption_error_message

    def get_article_image_link_title(self) -> (str, str):
        """
        Return the link title of the main article image and error to display in gui if there is one.
        :return: Return the link title of the main article image and error to display in gui if there is one.
        """
        return self._article_image_link_title, self._link_title_error_message

    def get_article_image_alt(self) -> (str, str):
        """
        Return the alt description of the main article image and error to display in gui if there is one.
        :return: Return the alt description of the main article image and error to display in gui if there is one.
        """
        return self._article_image_alt, self._image_alt_error_message

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

    def set_article_image_path(self, path: str) -> None:
        """
        Set the new main article image file path for the full version.
        Change modified attribute to True.
        :param path: New image path in disk.
        :return: None
        """
        self._article_full_image_path = path
        self.set_modified(True)

    def set_article_image_caption(self, text: str) -> None:
        """
        Set the new main article image caption.
        Change modified attribute to True.
        :param text: New image caption.
        :return: None
        """
        self._article_image_caption = text
        self.set_modified(True)

    def set_article_image_link_title(self, text: str) -> None:
        """
        Set the new main article image link title.
        Change modified attribute to True.
        :param text: New image link title.
        :return: None
        """
        self._article_image_link_title = text
        self.set_modified(True)

    def set_article_image_alt(self, text: str) -> None:
        """
        Set the new main article image alt description.
        Change modified attribute to True.
        :param text: New image alt description.
        :return: None
        """
        self._article_image_alt = text
        self.set_modified(True)
