class HtmlFile:
    """

    """
    TYPE_INDEX = 0
    TYPE_ARTICLE = 1
    TYPE_MENU = 2
    TYPE_CONTACT = 3
    TYPE_GALLERY = 4
    TYPE_MISC = 5
    TYPE_OTHER = 6

    __modified = False
    __path = None
    __name = None
    __file_type = None
    __parsed_html = None

    __title = None
    __description = None
    __keywords = None

    def __init__(self, name, path, file_type, parsed_html):
        self.__name = name
        self.__path = path
        self.__file_type = file_type
        self.__parsed_html = parsed_html

    def is_modified(self):
        return self.__modified

    def is_article(self):
        if self.__file_type == self.TYPE_ARTICLE:
            return True
        return False

    def is_menu(self):
        if self.__file_type == self.TYPE_MENU:
            return True
        return False

    def is_gallery(self):
        if self.__file_type == self.TYPE_GALLERY:
            return True
        return False

    def is_index(self):
        if self.__file_type == self.TYPE_INDEX:
            return True
        return False

    def is_misc(self):
        if self.__file_type == self.TYPE_INDEX:
            return True
        return False

    def is_contact(self):
        if self.__file_type == self.TYPE_CONTACT:
            return True
        return False

    def is_other(self):
        if self.__file_type == self.TYPE_OTHER:
            return True
        return False

    def get_name(self):
        return self.__name

    def get_path(self):
        return self.__path

    def get_parsed_html(self):
        return self.__parsed_html

    def get_type(self):
        return self.__file_type

    def get_title(self):
        return self.__title

    def get_description(self):
        return self.__description

    def get_keywords(self):
        return self.__keywords

    def set_title(self, title):
        self.__title = title

    def set_description(self, description):
        self.__description = description

    def set_keywords(self, keywords):
        self.__keywords = keywords

    def set_parsed_html(self, parsed_html):
        self.__parsed_html = parsed_html

    def set_modified(self, modified):
        self.__modified = modified

    def set_name(self, name):
        self.__name = name

    def __str__(self) -> str:
        return "White bear file {}, Type {}, Modified {}, Path {}, Title {}, Keywords {}, Description {}".\
            format(self.get_name(), self.__string_type(), self.is_modified(), self.get_path(), self.get_title(),
                   self.get_keywords(), self.get_description())

    def __string_type(self):
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
        else:
            return "index"
