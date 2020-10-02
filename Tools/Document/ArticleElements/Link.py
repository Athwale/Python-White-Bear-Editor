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
        self.text = text
        self.url = url
        self.title = title
        self.target = target_blank

    def seo_check_self(self):
        """
        Do a SEO check of this link.
        :return:
        """
        # TODO this