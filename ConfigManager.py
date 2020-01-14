import os
from typing import Dict, List, Tuple

from Constants.Strings import Strings
from Exceptions.AccessException import AccessException


class ConfigManager:
    """
    This class works with the persistent config file stored on disk which is used to remember last used values like
    last open directory and window position on the screen between editor uses.
    working directory - wd
    window position
    window size
    last open document
    """

    CONF_WORKING_DIR: str = 'wd'
    CONF_RECENT: str = 'last'
    CONF_POSITION: str = 'pos'

    def __init__(self):
        """

        """
        self.__conf_dict: Dict[str, object] = {}
        # If config file does not exist, create a new one
        self.__conf_file_path = Strings.editor_config_file
        if not os.path.exists(Strings.editor_config_file) or os.stat(self.__conf_file_path).st_size == 0:
            self.__create_new_config()
        if not os.access(self.__conf_file_path, os.R_OK) or not os.access(self.__conf_file_path, os.W_OK):
            raise AccessException(Strings.exception_conf_inaccessible)
        else:
            # Read the config file and store options in dictionary
            self.__read_config()

    def __create_new_config(self):
        """

        :return:
        """
        self.store_working_dir(Strings.home_directory)

    def __read_config(self):
        """

        :return:
        """
        with open(self.__conf_file_path, 'r') as config_file:
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
                        self.__conf_dict[self.CONF_WORKING_DIR] = Strings.home_directory
                    else:
                        self.__conf_dict[self.CONF_WORKING_DIR] = value
                elif name == self.CONF_POSITION:
                    try:
                        x_pos, y_pos = value.split(',', 1)
                        self.__conf_dict[self.CONF_POSITION] = (int(x_pos), int(y_pos))
                        # In case the position is damaged and can not be decoded, default to top left corner
                    except ValueError:
                        self.__conf_dict[self.CONF_POSITION] = (0, 0)
                elif name == self.CONF_RECENT:
                    # TODO more options
                    pass
                else:
                    # Ignore unknown options
                    continue

    def get_working_dir(self):
        """
        Get the last saved working directory.
        :return: String directory path to the saved last working directory.
        """
        return self.__conf_dict[self.CONF_WORKING_DIR]

    def get_window_position(self):
        """
        Get the last saved window position on screen.
        :return: Tuple of (x, y) position last saved when exiting the editor.
        """
        return self.__conf_dict[self.CONF_POSITION]

    def save_config_file(self):
        """
        Save the configuration stored in __conf_dict on disk drive in user's home.
        :return: None
        """
        # At this point after constructor, the config file exists and is full or empty but it is writeable.
        # This clears the file and writes new contents.
        with open(self.__conf_file_path, 'w') as conf_file:
            for name, value in self.__conf_dict.items():
                if name == self.CONF_POSITION:
                    conf_file.write(name + ' = ' + str(value[0]) + ',' + str(value[1]) + '\n')
                else:
                    conf_file.write(name + ' = ' + str(value) + '\n')

    def store_working_dir(self, path: str) -> None:
        """
        Save a new working directory into the dictionary
        :param path: New working directory path. This path is valid because it was chosen in a dialog window.
        :return: None
        """
        self.__conf_dict[self.CONF_WORKING_DIR] = path
        self.save_config_file()

    def store_window_position(self, pos1_pos2: Tuple[int, int]):
        """
        Save the last window position on screen into the dictionary.
        :param pos1_pos2: Tuple (x, y) of the left top corner of the window.
        :return: None
        """
        x, y = pos1_pos2
        self.__conf_dict[self.CONF_POSITION] = (x, y)
        self.save_config_file()
