from typing import List

from bs4 import BeautifulSoup


class SitemapGenerator:
    """
    Generates a sitemap.xml file based on page dictionaries
    """

    def __init__(self, pages: List[str]):
        """
        Constructor for the sitemap generator.
        :param pages: List of html page filenames.
        """
        self._pages = pages
        self._soup = BeautifulSoup()

    def create_sitemap(self) -> str:
        """
        Index must be present so it is assumed implicitly.
        :return: xml of the sitemap as a string.
        """