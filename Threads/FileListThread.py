import threading
import wx

from DirectoryLoader import DirectoryLoader
from Threads.Events.CarrierEvent import CarrierEvent
from Constants.Constants import Constants


class FileListThread(threading.Thread):
    """
    Gui objects must not be called from anywhere else than from the main gui thread. So use events to communicate with
    the main thread and send it results.
    """

    def __init__(self, parent, event_type: int, path: str):
        """
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
        Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        :return: List of pages to show in the listbox in gui.
        """
        page_dictionary = self._directory_loader.get_file_dict(self._path)
        file_list = sorted(page_dictionary.keys())
        result = CarrierEvent(self._event_type, -1, Constants.file_list_type, file_list)
        # The parent is the target that will receive the event, it is the gui.
        wx.PostEvent(self._parent, result)
