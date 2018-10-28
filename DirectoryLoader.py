import os
import glob

from Exceptions.AccessException import AccessException
from FileIdentifier import FileIdentifier
from Strings.Strings import Strings
from FileParser import FileParser


class DirectoryLoader:
    """This class loads and parses white bear root directory. The output is a dict of objects representing everything needed
    about the individual html files. If the directory is not readable or writable or the files are not, AccessException is
    thrown.
    """

    __directory_path = None
    __file_identifier = None
    __files = {}

    def __init__(self, directory_path):
        self.__directory_path = directory_path
        if self.is_white_bear_directory(directory_path):
            self.__file_identifier = FileIdentifier()
            self.__files = self.prepare_files(self.__directory_path)

    def get_file_dict(self):
        """

        :return:
        """
        return self.__files

    @staticmethod
    def is_white_bear_directory(path):
        """Checks whether chosen directory belongs to whitebear web.
        Throws: FileNotFoundError if index.html is not present
        Throws: IndexError if <title>White Bear is noy in index.html
        :param path:
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

    def prepare_files(self, path):
        """

        :param path:
        :return:
        """
        # Check all html files in directory are readable and writable
        os.chdir(path)
        files = {}
        parser = FileParser()
        for file in glob.glob("*.html"):
            if not os.access(file, os.R_OK) or not os.access(file, os.W_OK):
                raise AccessException(Strings.exception_access_html + " " + file)
            else:
                file_object = self.__file_identifier.create(os.path.realpath(file))
                parser.parse_file(file_object)
                # print(file_object)
                files[file] = file_object
        return files

