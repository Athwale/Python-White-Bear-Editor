import threading
from typing import List

import wx

from Tools.SitemapGenerator import SitemapGenerator


class SitemapThread(threading.Thread):
    """
    Creates a sitemap.
    """

    def __init__(self, parent, pages: List[str], work_dir: str, disable: bool):
        """
        Sitemap thread constructor.
        :param parent: The gui object that should receive the result.
        :param pages: List of pages to put into the sitemap.
        :param work_dir: Working directory of the editor. The sitemap and robots.txt will be saved there.
        :param disable: Leave editor disabled after thread finishes.
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._pages = pages
        self._work_dir = work_dir
        self._disable = disable
        self._generator = SitemapGenerator(self._pages)

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass a list of website names back into GUI.s
        """
        sitemap = self._generator.create_sitemap()
        wx.CallAfter(self._parent.on_sitemap_done, self, sitemap, self._disable)
