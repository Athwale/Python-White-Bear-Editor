import threading

import wx

from Constants.Constants import Numbers
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu


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
        # We know here that the document is modified because we are saving it.
        self._doc.set_status_color(Numbers.BLUE_COLOR)
        # This would turn the document red if something is wrong, but seo fail should not prevent save to disk, only
        # upload.
        if isinstance(self._doc, WhitebearDocumentArticle):
            self._doc.seo_test_self(self._config_manager.get_online_test())
            # TODO fail upload if seo error is detected.
        elif isinstance(self._doc, WhitebearDocumentMenu):
            self._doc.seo_test_self_basic()
        elif isinstance(self._doc, WhitebearDocumentIndex):
            # TODO seo/spell test other main index page texts, title, author, black text, red text
            self._doc.seo_test_self_basic()
        try:
            self._doc.convert_to_html()
            wx.CallAfter(self._parent.on_conversion_done, self, self._doc, self._save_as, self._disable)
        except UnrecognizedFileException as e:
            wx.CallAfter(self._parent.on_conversion_fail, e)
