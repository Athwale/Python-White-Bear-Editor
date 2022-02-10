import threading

import wx

from Constants.Constants import Numbers
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle


class ConvertorThread(threading.Thread):
    """
    Generates html contents from the internal document representation. The document can be an article, menu or index.
    """

    def __init__(self, parent, doc, save_as: bool, disable: bool):
        """
        Convertor thread constructor. This thread converts whitebear documents into html code.
        :param parent: The gui object that should receive the result.
        :param doc: The document to convert.
        :param save_as: Instructs the callback method to open a file dialog for the files.
        :param disable: Leave editor disabled after thread finishes.
        """
        threading.Thread.__init__(self)
        self._config_manager = ConfigManager.get_instance()
        self._parent = parent
        self._doc = doc
        self._save_as = save_as
        self._disable = disable

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.
        """
        if isinstance(self._doc, WhitebearDocumentArticle):
            self._doc.test_self(self._config_manager.get_online_test())
        else:
            self._doc.test_self()
        try:
            self._doc.convert_to_html()
            wx.CallAfter(self._parent.on_conversion_done, self, self._doc, self._save_as, self._disable)
        except UnrecognizedFileException as e:
            wx.CallAfter(self._parent.on_conversion_fail, e)
