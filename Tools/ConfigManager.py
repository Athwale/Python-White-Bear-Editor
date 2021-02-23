import os
from typing import List, Tuple

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Exceptions.AccessException import AccessException


class ConfigManager:
    """
    Singleton class.
    This class works with the persistent config file stored on disk which is used to remember last used values like
    last open directory and window position on the screen between editor uses.
    working directory - wd
    window position
    window size
    last open document
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
    CONF_SCRIPT: str = 'script'
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
        self._conf_dict = {}
        # If config file does not exist, create a new one
        self._conf_file_path = Strings.editor_config_file
        if not os.path.exists(Strings.editor_config_file) or os.stat(self._conf_file_path).st_size == 0:
            self._create_new_config()
        if not os.access(self._conf_file_path, os.R_OK) or not os.access(self._conf_file_path, os.W_OK):
            raise AccessException(Strings.exception_conf_inaccessible)
        else:
            # Read the config file and store options in dictionary
            self._read_config()

    def _create_new_config(self) -> None:
        """
        Create a new config file with a default working directory.
        :return: None
        """
        self.store_working_dir(Strings.home_directory)
        self.store_window_position((0, 0))
        self.store_window_size((Numbers.minimal_window_size_width, Numbers.minimal_window_size_height))
        self.store_global_title('')
        self.store_author(Strings.author)
        self.store_global_keywords('')
        self.store_main_page_description('')
        self.store_script('')
        self.store_black_text('')
        self.store_red_text('')

    def _read_config(self) -> None:
        """
        Parse configuration file form disk into a dictionary.
        :return:
        """
        with open(self._conf_file_path, 'r') as config_file:
            line: str
            for line in enumerate(config_file):
                if line[1].startswith('#'):
                    continue
                option: List[str] = line[1].split('=', 1)
                try:
                    name: str = option[0].strip()
                    value: str = option[1].strip()
                except IndexError:
                    # Ignore invalid options
                    continue

                if name == self.CONF_WORKING_DIR:
                    if not os.path.isdir(value) or not os.access(value, os.X_OK) \
                            or not os.access(value, os.R_OK or not os.access(value, os.W_OK)):
                        # Ignore working directory if not accessible, use default user home
                        self._conf_dict[self.CONF_WORKING_DIR] = Strings.home_directory
                    else:
                        self._conf_dict[self.CONF_WORKING_DIR] = value
                elif name == self.CONF_POSITION or name == self.CONF_SIZE:
                    try:
                        x_pos, y_pos = value.split(',', 1)
                        self._conf_dict[name] = (int(x_pos), int(y_pos))
                        # In case the position/size is damaged and can not be decoded, default to top left corner
                    except ValueError:
                        self._conf_dict[name] = (0, 0)
                else:
                    # Ignores unknown options.
                    if name in [self.CONF_LAST, self.CONF_GLOBAL_TITLE, self.CONF_AUTHOR, self.CONF_CONTACT,
                                self.CONF_KEYWORDS, self.CONF_DESCRIPTION, self.CONF_SCRIPT, self.CONF_BLACK_TXT,
                                self.CONF_RED_TXT]:
                        self._conf_dict[name] = value

    def save_config_file(self) -> None:
        """
        Save the configuration stored in _conf_dict on disk drive in user's home.
        :return: None
        """
        # At this point after constructor, the config file exists and is full or empty but it is writeable.
        # This clears the file and writes new contents.
        with open(self._conf_file_path, 'w') as conf_file:
            for name, value in self._conf_dict.items():
                if name == self.CONF_POSITION or name == self.CONF_SIZE:
                    conf_file.write(name + ' = ' + str(value[0]) + ',' + str(value[1]) + '\n')
                else:
                    conf_file.write(name + ' = ' + str(value) + '\n')

    def get_working_dir(self) -> str:
        """
        Get the last saved working directory.
        :return: String directory path to the saved last working directory.
        """
        return self._conf_dict[self.CONF_WORKING_DIR]

    def get_window_position(self) -> object:
        """
        Get the last saved window position on screen.
        :return: Tuple of (x, y) position last saved when exiting the editor.
        """
        return self._conf_dict[self.CONF_POSITION]

    def get_window_size(self) -> object:
        """
        Get the last saved window size on screen.
        :return: Tuple of (x, y) size last saved when exiting the editor.
        """
        return self._conf_dict[self.CONF_SIZE]

    def get_last_document(self) -> object:
        """
        Get the last opened document.
        :return: String name of the last opened document when exiting the editor. If no document was open, returns None.
        """
        if self.CONF_LAST not in self._conf_dict:
            return None
        return self._conf_dict[self.CONF_LAST]

    def get_global_title(self) -> str:
        """
        Get the global white-bear logo title.
        :return: The title.
        """
        return self._conf_dict[self.CONF_GLOBAL_TITLE]

    def get_author(self) -> str:
        """
        Get the author.
        :return: The author's signature.
        """
        return self._conf_dict[self.CONF_AUTHOR]

    def get_contact(self) -> str:
        """
        Get the contact string.
        :return: The contact string.
        """
        return self._conf_dict[self.CONF_CONTACT]

    def get_global_keywords(self) -> str:
        """
        Get the global meta keywords.
        :return: The global meta keywords.
        """
        return self._conf_dict[self.CONF_KEYWORDS]

    def get_main_meta_description(self) -> str:
        """
        Get the home page meta description.
        :return: The home page meta description.
        """
        return self._conf_dict[self.CONF_DESCRIPTION]

    def get_script(self) -> str:
        """
        Get the global script.
        :return: The script.
        """
        return self._conf_dict[self.CONF_SCRIPT]

    def get_main_page_black_text(self) -> str:
        """
        Get the main page black text.
        :return: The text.
        """
        return self._conf_dict[self.CONF_BLACK_TXT]

    def get_main_page_red_text(self) -> str:
        """
        Get the main page red text.
        :return: The text.
        """
        return self._conf_dict[self.CONF_RED_TXT]

    def store_working_dir(self, path: str) -> None:
        """
        Save a new working directory into the dictionary
        :param path: New working directory path. This path is valid because it was chosen in a dialog window.
        :return: None
        """
        self._conf_dict[self.CONF_WORKING_DIR] = path
        self.save_config_file()

    def store_window_position(self, pos1_pos2: Tuple[int, int]) -> None:
        """
        Save the last window position on screen into the dictionary.
        :param pos1_pos2: Tuple (x, y) of the left top corner of the window.
        :return: None
        """
        x, y = pos1_pos2
        self._conf_dict[self.CONF_POSITION] = (x, y)
        self.save_config_file()

    def store_window_size(self, size1_size2: Tuple[int, int]) -> None:
        """
        Save the last window size on screen into the dictionary.
        :param size1_size2: Tuple (x, y) of the size of the window.
        :return: None
        """
        x, y = size1_size2
        self._conf_dict[self.CONF_SIZE] = (x, y)
        self.save_config_file()

    def store_last_open_document(self, name: str) -> None:
        """
        Save the last opened document from editor into the dictionary.
        :param name: Name of the last opened website.
        :return: None
        """
        self._conf_dict[self.CONF_LAST] = name
        self.save_config_file()

    def store_global_title(self, title: str) -> None:
        """
        Save the default white-bear logo title into the dictionary.
        :param title: The global title.
        :return: None
        """
        self._conf_dict[self.CONF_GLOBAL_TITLE] = title
        self.save_config_file()

    def store_author(self, author: str) -> None:
        """
        Save the author signature into the dictionary.
        :param author: The author signature.
        :return: None
        """
        self._conf_dict[self.CONF_AUTHOR] = author
        self.save_config_file()

    def store_contact(self, contact: str) -> None:
        """
        Save the contact into the dictionary.
        :param contact: The contact.
        :return: None
        """
        self._conf_dict[self.CONF_CONTACT] = contact
        self.save_config_file()

    def store_global_keywords(self, keywords: str) -> None:
        """
        Save the global default meta keywords into the dictionary.
        :param keywords: The global default meta keywords.
        :return: None
        """
        self._conf_dict[self.CONF_KEYWORDS] = keywords
        self.save_config_file()

    def store_main_page_description(self, description: str) -> None:
        """
        Save the main page meta description into the dictionary.
        :param description: The meta description.
        :return: None
        """
        self._conf_dict[self.CONF_DESCRIPTION] = description
        self.save_config_file()

    def store_script(self, script: str) -> None:
        """
        Save the script into the dictionary.
        :param script: The script.
        :return: None
        """
        self._conf_dict[self.CONF_SCRIPT] = script
        self.save_config_file()

    def store_black_text(self, text: str) -> None:
        """
        Save the main page black text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._conf_dict[self.CONF_BLACK_TXT] = text
        self.save_config_file()

    def store_red_text(self, text: str) -> None:
        """
        Save the main page red text portion into the dictionary.
        :param text: The text.
        :return: None
        """
        self._conf_dict[self.CONF_RED_TXT] = text
        self.save_config_file()
