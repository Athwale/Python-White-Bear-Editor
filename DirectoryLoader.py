import os

from Exceptions.AccessException import AccessException
from Strings.Strings import Strings


class DirectoryLoader:
    """This class loads and parses white bear web root directory. The output is a dictionary of file names + path full
    to them on the system. If the directory is not readable or writable or the files are not readable or writeable,
    AccessException is raised.
    """

    def __init__(self):
        self.__directory_path = None
        self.__files = {}

    def get_file_dict(self, directory_path):
        """Return the read white bear directory as a dictionary of paths to files with file names as keys.
        :param directory_path: Path to the whitebear web root directory.
        :return: Dictionary {file name:path to the file}
        """
        self.__directory_path = directory_path
        if self.is_white_bear_directory(directory_path):
            self.__files = self.prepare_files(self.__directory_path)
        return self.__files

    @staticmethod
    def is_white_bear_directory(path):
        """Checks whether chosen directory belongs to the whitebear web.
        :raises FileNotFoundError if index.html is not present
        :raises IndexError if <title>White Bear is noy in index.html
        :raises AccessException if the directory can no be read or written to.
        :param path: Path to the root of the whitebear web directory.
        :return: True if path is an accessible white bear directory
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
        """Opens the path which should lead to a whitebear web root. Goes through all files which have to be readable
        and writeable and constructs a dictionary {file name:path to the file}.
        :raises AccessException if the files are not readable or not writeable.
        :param path: Path to the whitebear root directory.
        :return: Dictionary {file name:path to the file}
        """
        # Check all html files in directory are readable and writable
        files = {}
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                if not os.access(file, os.R_OK) or not os.access(file, os.W_OK):
                    raise AccessException(Strings.exception_access_html + " " + file)
                else:
                    files[file] = os.path.realpath(file)
        return files
