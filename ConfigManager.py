import os
from typing import Dict, List

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

    def __init__(self):
        """

        """
        self.__conf_dict: Dict[str, str] = {}
        # If config file does not exist, create a new one
        self.__conf_file_path = Strings.editor_config_file
        if not os.path.exists(Strings.editor_config_file):
            os.mknod(self.__conf_file_path)
        if not os.access(self.__conf_file_path, os.R_OK) or not os.access(self.__conf_file_path, os.W_OK):
            raise AccessException(Strings.exception_conf_inaccessible)
        else:
            # Read the config file and store options
            self.__read_config()

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
                    print(self.__conf_dict)
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

    def save_config_file(self):
        """
        Save the configuration stored in __conf_dict on disk drive in user's home.
        :return: None
        """
        # At this point after constructor, the config file exists and is full or empty but it is writeable.
        # This clears the file and writes new contents.
        with open(self.__conf_file_path, 'w') as conf_file:
            for name, value in self.__conf_dict.items():
                conf_file.write(name + ' = ' + value)

    def store_working_dir(self, path: str) -> None:
        """
        Save a new working directory into the dictionary
        :param path: New working directory path. This path is valid because it was chosen in a dialog window.
        :return: None
        """
        self.__conf_dict[self.CONF_WORKING_DIR] = path
        self.save_config_file()
