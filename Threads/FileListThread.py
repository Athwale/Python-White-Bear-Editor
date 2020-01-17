import threading


class FileListThread(threading.Thread):
    """
    Gui objects must not be called from anywhere else than from the main gui thread. So use events to communicate with
    the main thread and send it results.
    """

    def __init__(self, parent, path):
        """
        @param parent: The gui object that should receive the result.
        @param path: The path to whitebear web directory on disk.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._path = path

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        :return: List of pages to show in the listbox in gui.
        """
        pass