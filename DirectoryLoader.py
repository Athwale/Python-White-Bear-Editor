import os
import glob

from Exceptions.AccessException import AccessException
from Strings.Strings import Strings


class DirectoryLoader:
    """This class loads and parses white bear web root directory. The output is a dictionary of filenames + path to them
    on the system. If the directory is not readable or writable or the files are not readable or writeable,
    AccessException is raised.
    """

    __directory_path = None
    __files = {}

    def __init__(self, directory_path):
        self.__directory_path = directory_path
        if self.is_white_bear_directory(directory_path):
            self.__files = self.prepare_files(self.__directory_path)

    def get_file_dict(self):
        """Return the parsed white bear directory as a dictionary of HtmlFile objects identified by their names.
        :return: Dictionary {website name:HtmlFile object}
        """
        return self.__files

    @staticmethod
    def is_white_bear_directory(path):
        """Checks whether chosen directory belongs to a whitebear web.
        :raises FileNotFoundError if index.html is not present
        :raises IndexError if <title>White Bear is noy in index.html
        :param path: Path to the root of the whitebear web directory.
        :return: True if path is a white bear directory
        """
        if not os.access(path, os.R_OK) or not os.access(path, os.W_OK):
            raise AccessException(Strings.exception_access)

        # Check that file index.html is in directory and contains white bear string. The web will always have index.html
        try:
            # Open and automatically close after operation
            with open(os.path.join(path, "index.html"), "r") as index:
                if '<title>White Bear' not in index.read():
                    raise IndexError(Strings.exception_not_white_bear)
        except FileNotFoundError as ex:
            raise FileNotFoundError(ex, Strings.exception_index)
        return True

    @staticmethod
    def prepare_files(path):
        """
        :raises AccessException if files are not readable or not writeable.
        :param path: Path to the whitebear root directory.
        :return:
        """
        # Check all html files in directory are readable and writable
        os.chdir(path)
        files = {}
        for file in glob.glob("*"):
            if not os.access(file, os.R_OK) or not os.access(file, os.W_OK):
                raise AccessException(Strings.exception_access_html + " " + file)
            else:
                files[file] = os.path.realpath(file)
        return files
