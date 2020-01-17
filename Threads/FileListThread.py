import threading
import wx

from Threads.Events.CarrierEvent import CarrierEvent


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

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        :return: List of pages to show in the listbox in gui.
        """
        result = CarrierEvent(self._event_type, -1, self._path)
        # The parent is the target that will receive the event, it is the gui.
        wx.PostEvent(self._parent, result)
