import threading
from typing import List

import wx

from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Threads.ConvertorThread import ConvertorThread


class SavingThread(threading.Thread):
    """
    Manages other threads used for converting and saving documents to disk.
    """

    def __init__(self, parent, doc_list: List, save_as: bool, disable: bool):
        """
        Saving thread constructor. This thread manages saving sub threads and passes results to main gui.
        The purpose of this is to offload thread creation from main thread to speed up gui response.
        :param parent: The gui object that should receive the result.
        :param doc_list: The documents to save.
        :param save_as: Instructs the callback method to open a file dialog for the files.
        :param disable: Leave editor disabled after thread finishes.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._doc_list = doc_list
        self._save_as = save_as
        self._disable = disable

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.
        """
        for doc in self._doc_list:
            # Starting a lot of threads delays when the disable_editor shows in GUI if it runs in the main thread.
            convertor_thread = ConvertorThread(self, doc, self._save_as, self._disable)
            convertor_thread.start()

    def conversion_done(self, doc, save_as: bool, disable: bool) -> None:
        """
        Callback for when a file is successfully converted.
        :param doc: The document that was processed by the convertor thread.
        :param save_as: Open file dialog for the article and menu, otherwise save into the current filename.
        :param disable: Leave the editor disabled after threads finish.
        :return: None
        """
        wx.CallAfter(self._parent.on_conversion_done, doc, save_as, disable)

    def conversion_fail(self, e: UnrecognizedFileException) -> None:
        """
        Callback for when the convertor fails.
        :param e: Exception from the convertor thread.
        :return: None
        """
        wx.CallAfter(self._parent.on_conversion_fail, e)
