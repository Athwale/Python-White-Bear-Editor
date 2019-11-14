from Strings.Strings import Strings


class ParsedFile:
    """This class represents a parsed file belonging to the whitebear website. It contains all information associated
    with the file along with getters and setters for easy access and methods for working with the file.
    This is just a container for easy manipulation.
    """

    TYPE_INDEX = 0
    TYPE_ARTICLE = 1
    TYPE_MENU = 2
    TYPE_CONTACT = 3
    TYPE_GALLERY = 4
    TYPE_MISC = 5
    TYPE_CSS = 6
    TYPE_OTHER = 7

    def __init__(self, name, path, file_type, parsed_html):
        """Create a new ParsedFile object.
        :param name: Name of the parsed file.
        :param path: Full path on disk to the parsed file
        :param file_type: Type of the parsed file. Can be one of ParsedFile.TYPE_... types
        :param parsed_html: BeautifulSoup parsed html contents of the file.
        """
        self.__name = name
        self.__path = path
        self.__file_type = file_type
        self.__parsed_html = parsed_html
        self.__modified = False
        self.__title = None
        self.__description = None
        self.__keywords = None

    def is_modified(self):
        """Return True if this file was modified in the editor.
        :return: True if this file was modified in the editor.
        """
        return self.__modified

    def is_article(self):
        """Return True if this file is of type ParsedFile.TYPE_ARTICLE.
        :return: True if this file is of type ParsedFile.TYPE_ARTICLE.
        """
        if self.__file_type == self.TYPE_ARTICLE:
            return True
        return False

    def is_css(self):
        """Return True if this file is of type ParsedFile.TYPE_CSS.
        :return: True if this file is of type ParsedFile.TYPE_CSS.
        """
        if self.__file_type == self.TYPE_CSS:
            return True
        return False

    def is_menu(self):
        """Return True if this file is of type ParsedFile.TYPE_MENU.
        :return: True if this file is of type ParsedFile.TYPE_MENU.
        """
        if self.__file_type == self.TYPE_MENU:
            return True
        return False

    def is_gallery(self):
        """Return True if this file is of type ParsedFile.TYPE_GALLERY.
        :return: True if this file is of type ParsedFile.TYPE_GALLERY.
        """
        if self.__file_type == self.TYPE_GALLERY:
            return True
        return False

    def is_index(self):
        """Return True if this file is of type ParsedFile.TYPE_INDEX.
        :return: True if this file is of type ParsedFile.TYPE_INDEX.
        """
        if self.__file_type == self.TYPE_INDEX:
            return True
        return False

    def is_misc(self):
        """Return True if this file is of type ParsedFile.TYPE_MISC.
        :return: True if this file is of type ParsedFile.TYPE_MISC.
        """
        if self.__file_type == self.TYPE_INDEX:
            return True
        return False

    def is_contact(self):
        """Return True if this file is of type ParsedFile.TYPE_CONTACT.
        :return: True if this file is of type ParsedFile.TYPE_CONTACT.
        """
        if self.__file_type == self.TYPE_CONTACT:
            return True
        return False

    def is_other(self):
        """Return True if this file is of type ParsedFile.TYPE_OTHER.
        :return: True if this file is of type ParsedFile.TYPE_OTHER.
        """
        if self.__file_type == self.TYPE_OTHER:
            return True
        return False

    def get_name(self):
        """Return the file name.
        :return: Return the file name.
        """
        return self.__name

    def get_path(self):
        """Return the full file path on disk.
        :return: Return the full file path on disk.
        """
        return self.__path

    def get_parsed_html(self):
        """Return the parsed html contents.
        :return: Return the parsed html contents.
        """
        return self.__parsed_html

    def get_type(self):
        """Return the file type.
        :return: Return the file type.
        """
        return self.__file_type

    def get_title(self):
        """Return the title of the web page.
        :return: Return the title of the web page.
        """
        return self.__title

    def get_description(self):
        """Return the description of the web page.
        :return: Return the description of the web page.
        """
        return self.__description

    def get_keywords(self):
        """Return the keywords of the web page.
        :return: Return the keywords of the web page.
        """
        return self.__keywords

    def set_title(self, title):
        """Set the new title of the web page.
        Change modified attribute to True.
        :param title: New title for the web page.
        :return: None
        """
        self.__title = title
        self.set_modified(True)

    def set_description(self, description):
        """Set the new description of the web page.
        Change modified attribute to True.
        :param description: New description for the web page.
        :return: None
        """
        self.__description = description
        self.set_modified(True)

    def set_keywords(self, keywords):
        """Set the new keywords of the web page.
        Change modified attribute to True.
        :param keywords: New keywords for the web page.
        :return: None
        """
        self.__keywords = keywords
        self.set_modified(True)

    def set_parsed_html(self, parsed_html):
        """Set the new parsed html contents of the web page.
        Change modified attribute to True.
        :param parsed_html: New parsed html contents of the web page.
        :return: None
        """
        self.__parsed_html = parsed_html
        self.set_modified(True)

    def set_modified(self, modified):
        """Set the modified attribute.
        :raises TypeError if the new modified parameter is not bool.
        :param modified: New modified attribute state.
        :return: None
        """
        if isinstance(modified, bool):
            self.__modified = modified
        else:
            raise TypeError(Strings.exception_not_bool)

    def set_name(self, name):
        """Set the new name for the file.
        Change modified attribute to True.
        :param name: New name for the file..
        :return: None
        """
        self.__name = name
        self.set_modified(True)

    def __str__(self) -> str:
        return "White bear file {}, Type {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}". \
            format(self.get_name(), self.__string_type(), self.is_modified(), self.get_path(), self.get_title(),
                   self.get_keywords(), self.get_description())

    def __string_type(self):
        """Return a string human readable file type description.
        :return: A string human readable file type description.
        """
        if self.is_article():
            return "article"
        elif self.is_menu():
            return "menu"
        elif self.is_gallery():
            return "gallery"
        elif self.is_misc():
            return "misc"
        elif self.is_contact():
            return "contact"
        elif self.is_css():
            return "css"
        elif self.is_other():
            return "other file type"
        else:
            return "index"
