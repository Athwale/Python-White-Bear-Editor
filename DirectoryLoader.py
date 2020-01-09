import os
from typing import Dict
from Exceptions.AccessException import AccessException
from Constants.Strings import Strings
from bs4 import BeautifulSoup


class DirectoryLoader:
    """This class loads and parses white bear web root directory. The output is a dictionary of file names + path full
    to them on the system. If the directory is not readable or writable or the files are not readable or writeable,
    AccessException is raised.
    """

    def __init__(self):
        self.__directory_path: str = ''
        self.__files: Dict[str, str] = {}

    def get_file_dict(self, directory_path: str) -> Dict[str, str]:
        """Return the selected white bear directory as a dictionary of paths to files with file names as keys.
        :param directory_path: Path to the whitebear web root directory.
        :return: Dictionary {file name:path to the file}
        """
        self.__directory_path = directory_path
        if self.is_white_bear_directory(directory_path):
            self.__files = self.prepare_files(self.__directory_path)
        return self.__files

    @staticmethod
    def is_white_bear_directory(path: str) -> bool:
        """Checks whether chosen directory belongs to the whitebear web.
        :raises FileNotFoundError if index.html is not present
        :raises IndexError if <title>White Bear is noy in index.html
        :raises AccessException if the directory can no be read or written to.
        :param path: Path to the root of the whitebear web directory.
        :return: True if path is an accessible white bear directory
        """
        if not os.access(path, os.R_OK) or not os.access(path, os.W_OK):
            raise AccessException(Strings.exception_access)

        if not os.path.exists(os.path.join(path, 'index.html')):
            raise IndexError(Strings.exception_not_white_bear)
        else:
            with open(os.path.join(path, 'index.html'), 'r') as index:
                parsed_index: BeautifulSoup = BeautifulSoup(index, 'html5lib')
                if len(parsed_index.find_all('article', class_='indexPage')) != 1:
                    raise IndexError(Strings.exception_not_white_bear)
                else:
                    return True

    @staticmethod
    def prepare_files(path: str) -> Dict[str, str]:
        """Opens the path which should lead to a whitebear web root. Goes through all files which have to be readable
        and writeable and constructs a dictionary {file name:path to the file}.
        :raises AccessException if the files are not readable or not writeable.
        :param path: Path to the whitebear root directory.
        :return: Dictionary {file name:path to the file}
        """
        # Check all html files in directory are readable and writable
        files: Dict[str, str] = {}
        file: str
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                if not os.access(file, os.R_OK) or not os.access(file, os.W_OK):
                    raise AccessException(Strings.exception_access_html + " " + file)
                else:
                    files[file] = os.path.realpath(file)
        return files
