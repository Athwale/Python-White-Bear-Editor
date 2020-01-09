import os
from Constants.Strings import Strings
from Exceptions.AccessException import AccessException

# Vsechno do slovniku v pameti, ukladat cely slovnik
class ConfigManager:
    """
    This class works with the persistent config file stored on disk which is used to remember last used values like
    last open directory and window position on the screen between editor uses.
    """

    def __init__(self):
        # If config file does not exist, create a new one
        self.conf_file = Strings.editor_config_file
        if not os.path.exists(Strings.editor_config_file):
            os.mknod(self.conf_file)
        else:
            if not os.access(self.conf_file, os.R_OK) or not os.access(self.conf_file, os.W_OK):
                raise AccessException(Strings.exception_conf_inaccessible)

    def store_working_dir(self, path):
        """

        :param path:
        :return:
        """
        with open(self.conf_file) as conf_file:
            pass
