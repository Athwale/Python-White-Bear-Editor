from typing import Tuple, Dict

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from Constants.Constants import Numbers
from Constants.Constants import Strings


class ConfigManager:
    """
    Singleton class.
    This class works with the persistent config file stored on disk which is used to remember last used values.
    """
    __instance = None
    CONF_LAST_DIR: str = 'lastDir'
    CONF_WORKING_DIR: str = 'wd'
    CONF_LAST: str = 'last'
    CONF_POSITION: str = 'pos'
    CONF_SIZE: str = 'size'

    CONF_GLOBAL_TITLE: str = 'title'
    CONF_AUTHOR: str = 'author'
    CONF_CONTACT: str = 'contact'
    CONF_KEYWORDS: str = 'keywords'
    CONF_DESCRIPTION: str = 'mainDescription'
    CONF_SCRIPT: str = 'global_script'
    CONF_BLACK_TXT: str = 'blackTxt'
    CONF_RED_TXT: str = 'redTxt'
    CONF_NEWS: str = 'news'

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ConfigManager.__instance is None:
            ConfigManager()
        return ConfigManager.__instance

    def __init__(self):
        """
        Constructor for config manager.
        """
        if ConfigManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ConfigManager.__instance = self
        self._dir_conf: Dict[str, str] = {}
        self._whole_conf = {}
        self._load()

    def _create_new_dir_config(self) -> Dict[str, str]:
        """
        Create a new config file with default values.
        :return: New configuration dictionary.
        """
        return {self.CONF_WORKING_DIR: Strings.home_directory,
                self.CONF_POSITION: '0,0',
                self.CONF_SIZE: str(Numbers.minimal_window_size_width) + ',' + str(Numbers.minimal_window_size_height),
                self.CONF_GLOBAL_TITLE: '',
                self.CONF_AUTHOR: Strings.author,
                self.CONF_CONTACT: '',
                self.CONF_KEYWORDS: '',
                self.CONF_DESCRIPTION: '',
                self.CONF_SCRIPT: '',
                self.CONF_BLACK_TXT: '',
                self.CONF_RED_TXT: '',
                self.CONF_NEWS: str(Numbers.default_news)}

    def _init_config(self) -> None:
        """
        Create a new default config file.
        :return: None
        """
        self._dir_conf = self._create_new_dir_config()
        self._whole_conf = {self.CONF_LAST_DIR: Strings.home_directory, Strings.home_directory: self._dir_conf}
        self.save_config_file()

    def _load(self) -> None:
        """
        Open and parse a yaml config file, create a new empty file if the current file is broken.
        :return: None
        :raises PermissionError if config file is not readable.
        """
        try:
            with open(Strings.editor_config_file, "r") as yml:
                self._whole_conf = yaml.safe_load(yml)
                if not self._whole_conf:
                    self._init_config()
        except (ParserError, ScannerError, FileNotFoundError, KeyError) as _:
            # Create a new default valid yaml config file.
            self._init_config()

    def save_config_file(self) -> None:
        """
        Save the configuration onto disk drive in user's home.
        :return: None
        """
        # At this point after constructor, the config file exists and is full or empty but it is writeable.
        # This clears the file and writes new contents.
        with open(Strings.editor_config_file, 'w') as file:
            yaml.dump(self._whole_conf, file)

    def check_config(self) -> bool:
        """
        Check the loaded config for missing values.
        :return: False if any value is missing.
        """
        # todo check all keywords present for all new params.
        correct = True
        for name in [self.CONF_WORKING_DIR, self.CONF_GLOBAL_TITLE, self.CONF_AUTHOR, self.CONF_CONTACT,
                     self.CONF_KEYWORDS, self.CONF_DESCRIPTION, self.CONF_SCRIPT, self.CONF_BLACK_TXT,
                     self.CONF_RED_TXT, self.CONF_NEWS]:
            try:
                if not self._dir_conf[name]:
                    correct = False
            except KeyError:
                # Repair the config and report error.
                correct = False
                self._dir_conf[name] = ''
        return correct

    def set_active_dir(self, path: str) -> bool:
        """
        Select which working directory from the config file is active.
        :param path: The directory path.
        :return: True if the requested directory is in the config.
        """
        try:
            self._dir_conf = self._whole_conf[path]
        except KeyError:
            return False
        return True

    def add_directory(self, path: str) -> None:
        """
        Add another working directory config into the yaml file.
        :param path: The working directory path.
        :return: None
        """
        new_config = self._create_new_dir_config()
        new_config[self.CONF_WORKING_DIR] = path
        self._whole_conf[path] = new_config

    def get_last_directory(self) -> str:
        """
        Return the path to the last known opened whitebear directory.
        :return: The path to the last known opened whitebear directory.
        """
        return self._whole_conf[self.CONF_LAST_DIR]

    def get_working_dir(self) -> str:
        """
        Get the working directory name.
        :return: String directory path to the working directory.
        """
        return self._dir_conf[self.CONF_WORKING_DIR]

    def get_window_position(self) -> object:
        """
        Get the last saved window position on screen.
        :return: Tuple of (x, y) position last saved when exiting the editor.
        """
        try:
            position = self._dir_conf[self.CONF_POSITION].split(',', 1)
        except KeyError:
            # Config damaged, return a default position.
            position = (0, 0)
        return int(position[0]), int(position[1])

    def get_window_size(self) -> object:
        """
        Get the last saved window size on screen.
        :return: Tuple of (x, y) size last saved when exiting the editor.
        """
        try:
            size = self._dir_conf[self.CONF_SIZE].split(',', 1)
        except KeyError:
            # Config damaged, return a default size.
            size = (Numbers.minimal_window_size_width, Numbers.minimal_window_size_height)
        return int(size[0]), int(size[1])

    def get_last_document(self) -> object:
        """
        Get the last opened document.
        :return: String name of the last opened document when exiting the editor. If no document was open, returns None.
        """
        if self.CONF_LAST not in self._dir_conf:
            return None
        return self._dir_conf[self.CONF_LAST]

    def get_global_title(self) -> str:
        """
        Get the global white-bear logo title.
        :return: The title.
        """
        return self._dir_conf[self.CONF_GLOBAL_TITLE]

    def get_author(self) -> str:
        """
        Get the author.
        :return: The author's signature.
        """
        return self._dir_conf[self.CONF_AUTHOR]

    def get_contact(self) -> str:
        """
        Get the contact string.
        :return: The contact string.
        """
        return self._dir_conf[self.CONF_CONTACT]

    def get_global_keywords(self) -> str:
        """
        Get the global meta keywords.
        :return: The global meta keywords.
        """
        return self._dir_conf[self.CONF_KEYWORDS]

    def get_main_meta_description(self) -> str:
        """
        Get the home page meta description.
        :return: The home page meta description.
        """
        return self._dir_conf[self.CONF_DESCRIPTION]

    def get_script(self) -> str:
        """
        Get the global script.
        :return: The script.
        """
        return self._dir_conf[self.CONF_SCRIPT]

    def get_main_page_black_text(self) -> str:
        """
        Get the main page black text.
        :return: The text.
        """
        return self._dir_conf[self.CONF_BLACK_TXT]

    def get_main_page_red_text(self) -> str:
        """
        Get the main page red text.
        :return: The text.
        """
        return self._dir_conf[self.CONF_RED_TXT]

    def get_number_of_news(self) -> int:
        """
        Return how many latest articles to display on home page.
        :return: How many latest articles to display on home page.
        """
        try:
            return int(self._dir_conf[self.CONF_NEWS])
        except ValueError as _:
            self._dir_conf[self.CONF_NEWS] = str(Numbers.default_news)
            return Numbers.default_news

    def store_working_dir(self, path: str) -> None:
        """
        Save a new working directory into the dictionary
        :param path: New working directory path. This path is valid because it was chosen in a dialog window.
        :return: None
        """
        self._whole_conf[self.CONF_LAST_DIR] = path
        self._dir_conf[self.CONF_WORKING_DIR] = path
        self.save_config_file()

    def remove_config_dir(self, path: str) -> None:
        """
        Remove configuration of a directory.
        :param path: The path to the directory
        :return: None
        """
        del self._whole_conf[path]
        self.save_config_file()

    def store_window_position(self, pos1_pos2: Tuple[int, int]) -> None:
        """
        Save the last window position on screen into the dictionary.
        :param pos1_pos2: Tuple (x, y) of the left top corner of the window.
        :return: None
        """
        x, y = pos1_pos2
        self._dir_conf[self.CONF_POSITION] = str(x) + ',' + str(y)
        self.save_config_file()

    def store_window_size(self, size1_size2: Tuple[int, int]) -> None:
        """
        Save the last window size on screen into the dictionary.
        :param size1_size2: Tuple (x, y) of the size of the window.
        :return: None
        """
        x, y = size1_size2
        self._dir_conf[self.CONF_SIZE] = str(x) + ',' + str(y)
        self.save_config_file()

    def store_last_open_document(self, name: str) -> None:
        """
        Save the last opened document from editor into the dictionary.
        :param name: Name of the last opened website.
        :return: None
        """
        self._dir_conf[self.CONF_LAST] = name
        self.save_config_file()

    def store_global_title(self, title: str) -> bool:
        """
        Save the default white-bear logo title into the dictionary.
        :param title: The global title.
        :return: True if stored value was changed.
        """
        if self._dir_conf[self.CONF_GLOBAL_TITLE] != title:
            self._dir_conf[self.CONF_GLOBAL_TITLE] = title
            self.save_config_file()
            return True
        return False

    def store_author(self, author: str) -> bool:
        """
        Save the author signature into the dictionary.
        :param author: The author signature.
        :return: True if stored value was changed.
        """
        if self._dir_conf[self.CONF_AUTHOR] != author:
            self._dir_conf[self.CONF_AUTHOR] = author
            self.save_config_file()
            return True
        return False

    def store_contact(self, contact: str) -> None:
        """
        Save the contact into the dictionary.
        :param contact: The contact.
        :return: None
        """
        self._dir_conf[self.CONF_CONTACT] = contact
        self.save_config_file()

    def store_global_keywords(self, keywords: str) -> None:
        """
        Save the global default meta keywords into the dictionary.
        :param keywords: The global default meta keywords.
        :return: None
        """
        self._dir_conf[self.CONF_KEYWORDS] = keywords
        self.save_config_file()

    def store_main_page_description(self, description: str) -> None:
        """
        Save the main page meta description into the dictionary.
        :param description: The meta description.
        :return: None
        """
        self._dir_conf[self.CONF_DESCRIPTION] = description
        self.save_config_file()

    def store_script(self, script: str) -> bool:
        """
        Save the script into the dictionary.
        :param script: The script.
        :return: True if stored value was changed,
        """
        if self._dir_conf[self.CONF_SCRIPT] != script:
            self._dir_conf[self.CONF_SCRIPT] = script
            self.save_config_file()
            return True
        return False

    def store_black_text(self, text: str) -> None:
        """
        Save the main page black text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._dir_conf[self.CONF_BLACK_TXT] = text
        self.save_config_file()

    def store_red_text(self, text: str) -> None:
        """
        Save the main page red text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._dir_conf[self.CONF_RED_TXT] = text
        self.save_config_file()

    def store_number_of_news(self, news: int) -> None:
        """
        Save the the number of latest articles to display into the dictionary.
        :param news: The number of articles.
        :return: None
        """
        self._dir_conf[self.CONF_NEWS] = str(news)
        self.save_config_file()
