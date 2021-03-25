from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from Constants.Constants import Strings
from Tools.ConfigManager import ConfigManager


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
        self._soup = BeautifulSoup(features='xml')
        self._config_manager: ConfigManager = ConfigManager.get_instance()

    def create_sitemap(self) -> str:
        """
        Creates a string xml code of the sitemap.
        :return: xml of the sitemap as a string.
        """
        urlset_tag = self._soup.new_tag('urlset', attrs={'xmlns': Strings.sitemap_xmlns})
        self._soup.append(urlset_tag)
        page_url = self._config_manager.get_url()
        for page in self._pages:
            url_tag = self._soup.new_tag('url')
            # Location
            loc_tag = self._soup.new_tag('loc')
            loc_tag.string = page_url + '/' + str(page)
            url_tag.append(loc_tag)
            # Last modification
            lastmod_tag = self._soup.new_tag('lastmod')
            # Just use today for all.
            lastmod_tag.string = datetime.now().strftime("%Y-%m-%d")
            url_tag.append(lastmod_tag)
            # Change frequency
            changefreq_tag = self._soup.new_tag('changefreq')
            changefreq_tag.string = Strings.change_frequency
            url_tag.append(changefreq_tag)
            urlset_tag.append(url_tag)

        self._soup.append(urlset_tag)
        return str(self._soup.prettify())
