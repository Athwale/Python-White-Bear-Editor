from Tools.Document.ArticleElements.Text import Text


class Heading:
    """
    Represents a h3 or h4 heading. Consists of a single instance of Text.
    """

    SIZE_H3 = 3
    SIZE_H4 = 4

    def __init__(self, text: Text, size: int):
        """
        Constructor for a new heading
        :param text: The text of the heading
        :param size: Either Heading.SIZE_H3 or Heading.SIZE_H4.
        """
        self._text = text
        self._size = size

    def get_text(self) -> Text:
        """
        Get the text of this Heading.
        :return: The text of this Heading.
        """
        return self._text

    def get_size(self) -> int:
        """
        Get the size of this Heading ('Heading.SIZE_H3' or 'Heading.SIZE_H4').
        :return: The size of this Heading.
        """
        return self._size
