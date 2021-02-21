import threading

import wx

from Constants.Constants import Numbers
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle


class ConvertorThread(threading.Thread):
    """
    Generates html contents from the internal document representation.
    """

    def __init__(self, parent, doc: WhitebearDocumentArticle):
        """
        Filelist thread constructor. This thread parses a supposed WhiteBear web directory and passes a list of
        websites back into the GUI.
        @param parent: The gui object that should receive the result.
        @param doc: The document to convert.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._doc = doc

    def run(self):
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.s
        """
        # We know here that the document is modified because we are saving it.
        self._doc.set_status_color(Numbers.BLUE_COLOR)
        # This would turn the document red if something is wrong, but seo fail should not prevent save to disk, only
        # upload.
        self._doc.seo_test_self()
        try:
            article: str = self._doc.convert_to_html()
            menu: str = self._doc.get_menu_section().convert_to_html()
            wx.CallAfter(self._parent.on_conversion_done, article, menu)
        except UnrecognizedFileException as e:
            wx.CallAfter(self._parent.on_conversion_fail, e)
