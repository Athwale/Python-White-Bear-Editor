class Link:
    """
    Represents a link inside text.
    """

    def __init__(self, text: str, url: str, title: str, target_blank: bool):
        """
        Constructor for a Link.
        :param text: The visible text of the link.
        :param url: The URL of the link.
        :param title: The html title of the link.
        :param target_blank: True if the link has target blank set.
        """
        self._text = text
        self._url = url
        self._title = title
        self._target = target_blank

    def seo_check_self(self):
        """
        Do a SEO check of this link.
        :return:
        """
        # TODO this

    def get_text(self) -> str:
        """
        Return the visible text of the link.
        :return: the visible text of the link.
        """
        return self._text

    def get_url(self) -> str:
        """
        Return the url of the link.
        :return: the url of the link.
        """
        return self._url

    def get_title(self) -> str:
        """
        Return the title of the link.
        :return: the title of the link.
        """
        return self._title

    def target_blank(self) -> bool:
        """
        Return True if the link is set to open in a new page.
        :return: True if the link is set to open in a new page.
        """
        return self._target

    def set_text(self, text: str) -> None:
        """
        Set a new visible text for the link.
        :param text: The new text to display.
        :return: None
        """
        self._text = text

    def set_url(self, url: str) -> None:
        """
        Set a new url for the link.
        :param url: The new url.
        :return: None
        """
        self._url = url

    def set_title(self, title: str) -> None:
        """
        Set a new title for the link.
        :param title: The new title.
        :return: None
        """
        self._title = title

    def set_target(self, blank: bool) -> None:
        """
        Set whether the link opens a page in a new window.
        :param blank: True if the link opens in a new window.
        :return: None
        """
        self._target = blank
