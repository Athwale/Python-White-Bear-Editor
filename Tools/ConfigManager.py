import yaml
from typing import Tuple, Dict
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
        self._yaml_conf: Dict[str, str] = {}
        self._load()

    def _create_new_config(self) -> Dict[str, str]:
        """
        Create a new config file with default values.
        :return: New configuration dictionary.
        """
        return {self.CONF_WORKING_DIR: Strings.home_directory,
                self.CONF_POSITION: '0,0',
                self.CONF_SIZE: str(Numbers.minimal_window_size_width) + ',' +
                str(Numbers.minimal_window_size_height),
                self.CONF_GLOBAL_TITLE: '',
                self.CONF_AUTHOR: Strings.author,
                self.CONF_CONTACT: '',
                self.CONF_KEYWORDS: '',
                self.CONF_DESCRIPTION: '',
                self.CONF_SCRIPT: '',
                self.CONF_BLACK_TXT: '',
                self.CONF_RED_TXT: ''}

    def _load(self) -> None:
        """
        Open and parse a yaml config file, create a new empty file if the current file is broken.
        :return: None
        :raises PermissionError if config file is not readable.
        """
        try:
            with open(Strings.editor_config_file, "r") as yml:
                self._yaml_conf = yaml.safe_load(yml)
        except (ParserError, ScannerError, FileNotFoundError) as _:
            # Create a new default valid yaml config file.
            self._yaml_conf = self._create_new_config()
            self.save_config_file()

    def save_config_file(self) -> None:
        """
        Save the configuration stored in _yaml_conf on disk drive in user's home.
        :return: None
        """
        # At this point after constructor, the config file exists and is full or empty but it is writeable.
        # This clears the file and writes new contents.
        with open(Strings.editor_config_file, 'w') as file:
            yaml.dump(self._yaml_conf, file)

    def check_config(self) -> bool:
        """
        Check the loaded config for missing values.
        :return: False if any value is missing.
        """
        for name, value in self._yaml_conf.items():
            if not value:
                return False
        return True

    def get_working_dir(self) -> str:
        """
        Get the last saved working directory.
        :return: String directory path to the saved last working directory.
        """
        return self._yaml_conf[self.CONF_WORKING_DIR]

    def get_window_position(self) -> object:
        """
        Get the last saved window position on screen.
        :return: Tuple of (x, y) position last saved when exiting the editor.
        """
        position = self._yaml_conf[self.CONF_POSITION].split(',', 1)
        return int(position[0]), int(position[1])

    def get_window_size(self) -> object:
        """
        Get the last saved window size on screen.
        :return: Tuple of (x, y) size last saved when exiting the editor.
        """
        size = self._yaml_conf[self.CONF_SIZE].split(',', 1)
        return int(size[0]), int(size[1])

    def get_last_document(self) -> object:
        """
        Get the last opened document.
        :return: String name of the last opened document when exiting the editor. If no document was open, returns None.
        """
        if self.CONF_LAST not in self._yaml_conf:
            return None
        return self._yaml_conf[self.CONF_LAST]

    def get_global_title(self) -> str:
        """
        Get the global white-bear logo title.
        :return: The title.
        """
        return self._yaml_conf[self.CONF_GLOBAL_TITLE]

    def get_author(self) -> str:
        """
        Get the author.
        :return: The author's signature.
        """
        return self._yaml_conf[self.CONF_AUTHOR]

    def get_contact(self) -> str:
        """
        Get the contact string.
        :return: The contact string.
        """
        return self._yaml_conf[self.CONF_CONTACT]

    def get_global_keywords(self) -> str:
        """
        Get the global meta keywords.
        :return: The global meta keywords.
        """
        return self._yaml_conf[self.CONF_KEYWORDS]

    def get_main_meta_description(self) -> str:
        """
        Get the home page meta description.
        :return: The home page meta description.
        """
        return self._yaml_conf[self.CONF_DESCRIPTION]

    def get_script(self) -> str:
        """
        Get the global script.
        :return: The script.
        """
        return self._yaml_conf[self.CONF_SCRIPT]

    def get_main_page_black_text(self) -> str:
        """
        Get the main page black text.
        :return: The text.
        """
        return self._yaml_conf[self.CONF_BLACK_TXT]

    def get_main_page_red_text(self) -> str:
        """
        Get the main page red text.
        :return: The text.
        """
        return self._yaml_conf[self.CONF_RED_TXT]

    def store_working_dir(self, path: str) -> None:
        """
        Save a new working directory into the dictionary
        :param path: New working directory path. This path is valid because it was chosen in a dialog window.
        :return: None
        """
        self._yaml_conf[self.CONF_WORKING_DIR] = path
        self.save_config_file()

    def store_window_position(self, pos1_pos2: Tuple[int, int]) -> None:
        """
        Save the last window position on screen into the dictionary.
        :param pos1_pos2: Tuple (x, y) of the left top corner of the window.
        :return: None
        """
        x, y = pos1_pos2
        self._yaml_conf[self.CONF_POSITION] = str(x) + ',' + str(y)
        self.save_config_file()

    def store_window_size(self, size1_size2: Tuple[int, int]) -> None:
        """
        Save the last window size on screen into the dictionary.
        :param size1_size2: Tuple (x, y) of the size of the window.
        :return: None
        """
        x, y = size1_size2
        self._yaml_conf[self.CONF_SIZE] = str(x) + ',' + str(y)
        self.save_config_file()

    def store_last_open_document(self, name: str) -> None:
        """
        Save the last opened document from editor into the dictionary.
        :param name: Name of the last opened website.
        :return: None
        """
        self._yaml_conf[self.CONF_LAST] = name
        self.save_config_file()

    def store_global_title(self, title: str) -> None:
        """
        Save the default white-bear logo title into the dictionary.
        :param title: The global title.
        :return: None
        """
        self._yaml_conf[self.CONF_GLOBAL_TITLE] = title
        self.save_config_file()

    def store_author(self, author: str) -> None:
        """
        Save the author signature into the dictionary.
        :param author: The author signature.
        :return: None
        """
        self._yaml_conf[self.CONF_AUTHOR] = author
        self.save_config_file()

    def store_contact(self, contact: str) -> None:
        """
        Save the contact into the dictionary.
        :param contact: The contact.
        :return: None
        """
        self._yaml_conf[self.CONF_CONTACT] = contact
        self.save_config_file()

    def store_global_keywords(self, keywords: str) -> None:
        """
        Save the global default meta keywords into the dictionary.
        :param keywords: The global default meta keywords.
        :return: None
        """
        self._yaml_conf[self.CONF_KEYWORDS] = keywords
        self.save_config_file()

    def store_main_page_description(self, description: str) -> None:
        """
        Save the main page meta description into the dictionary.
        :param description: The meta description.
        :return: None
        """
        self._yaml_conf[self.CONF_DESCRIPTION] = description
        self.save_config_file()

    def store_script(self, script: str) -> None:
        """
        Save the script into the dictionary.
        :param script: The script.
        :return: None
        """
        self._yaml_conf[self.CONF_SCRIPT] = script
        self.save_config_file()

    def store_black_text(self, text: str) -> None:
        """
        Save the main page black text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._yaml_conf[self.CONF_BLACK_TXT] = text
        self.save_config_file()

    def store_red_text(self, text: str) -> None:
        """
        Save the main page red text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._yaml_conf[self.CONF_RED_TXT] = text
        self.save_config_file()
