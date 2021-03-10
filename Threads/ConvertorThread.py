import threading

import wx

from Constants.Constants import Numbers
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle


class ConvertorThread(threading.Thread):
    """
    Generates html contents from the internal document representation. The document can be an article, menu or index.
    """

    def __init__(self, parent, doc, save_as: bool, disable: bool):
        """
        Filelist thread constructor. This thread parses a supposed WhiteBear web directory and passes a list of
        websites back into the GUI.
        :param parent: The gui object that should receive the result.
        :param doc: The document to convert.
        :param save_as: Instructs the callback method to open a file dialog for the files.
        :param disable: Leave editor disabled after thread finishes.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._doc = doc
        self._save_as = save_as
        self._disable = disable

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.s
        """
        # We know here that the document is modified because we are saving it.
        self._doc.set_status_color(Numbers.BLUE_COLOR)
        # This would turn the document red if something is wrong, but seo fail should not prevent save to disk, only
        # upload.
        if isinstance(self._doc, WhitebearDocumentArticle):
            self._doc.seo_test_self()
        try:
            self._doc.convert_to_html()
            wx.CallAfter(self._parent.on_conversion_done, self._doc, self._save_as, self._disable)
        except UnrecognizedFileException as e:
            wx.CallAfter(self._parent.on_conversion_fail, e)
