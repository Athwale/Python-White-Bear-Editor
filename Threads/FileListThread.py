import threading

import wx

from Tools.DirectoryLoader import DirectoryLoader
from Exceptions.AccessException import AccessException
from Exceptions.UnrecognizedFileException import UnrecognizedFileException

class FileListThread(threading.Thread):
    """
    Gui objects must not be called from anywhere else than from the main gui thread. So use events to communicate with
    the main thread and send it results.
    """

    def __init__(self, parent, event_type: int, path: str):
        """
        Filelist thread constructor. This thread parses a supposed WhiteBear web directory and passes a list of
        websites back into the GUI.
        @param parent: The gui object that should receive the result.
        @param path: The path to whitebear web directory on disk.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._event_type = event_type
        self._path = path
        self._directory_loader = DirectoryLoader()

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.s
        """
        try:
            self._directory_loader.load_directory(self._path)
            file_list = sorted(self._directory_loader.get_articles().keys())
            # The CallAfter method functions as a carrier between threads, the callable function passed into the method
            # will be called in the main GUI thread. This passes an event into the main thread in background which is
            # processed normally in the wx main thread queue.
            wx.CallAfter(self._parent.on_filelist_loaded, file_list)
        except (AccessException, IndexError, FileNotFoundError, UnrecognizedFileException) as e:
            wx.CallAfter(self._parent.on_filelist_load_fail, e)
