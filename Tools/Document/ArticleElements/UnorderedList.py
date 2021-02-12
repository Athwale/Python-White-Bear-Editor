from typing import List

from Tools.Document.ArticleElements.Paragraph import Paragraph


class UnorderedList:
    """
    Represents a list in the page. Consists of Paragraph instances.
    """

    def __init__(self):
        """
        Constructor for a new UnorderedList.
        """
        self._items = []

    def append_paragraph(self, item: Paragraph) -> None:
        """
        Append a new Paragraph item to the list.
        :param item: The new Paragraph instance to append.
        :return: None
        """
        self._items.append(item)

    def get_paragraphs(self) -> List[Paragraph]:
        """
        Return the list of Paragraphs that this UnorderedList holds.
        :return: the list of Paragraphs that this UnorderedList holds.
        """
        return self._items

    def __str__(self) -> str:
        return 'Unordered list: ' + str(self._items)
