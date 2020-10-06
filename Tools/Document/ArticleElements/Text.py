class Text:
    """
    This class represents a piece of text which can be colored and bold.
    """

    def __init__(self, text: str, bold: bool, color: str):
        """
        Constructor for a new text piece.
        :param text: The text of this Text.
        :param bold: True if the text is bold.
        :param color: The string color defined in css of this text or black.
        """
        self._text = text
        self._bold = bold
        self._color = color

    def get_text(self) -> str:
        """
        Get the text of this Text.
        :return: The text of this Text
        """
        return self._text

    def get_color(self) -> str:
        """
        Get the text color.
        :return: The text color of this Text
        """
        return self._color

    def is_bold(self) -> bool:
        """
        Get the text boldness.
        :return: The text boldness of this Text
        """
        return self._bold


class Break:
    """
    Represents a line break but not a new paragraph start.
    """
    pass
