from typing import List

from Tools.Document.ArticleElements.Link import Link


class Paragraph:
    """
    This class represents one paragraph in a article. A paragraph consists of a list of instances of text, break and
    link.
    """

    def __init__(self):
        """
        Constructor for paragraph.
        """
        self._elements_list = []

    def add_element(self, text_element) -> None:
        """
        Add an element to this paragraph. This can be Text or Link.
        :param text_element: The element to add.
        :return: None
        """
        self._elements_list.append(text_element)

    def extend_elements(self, paragraph) -> None:
        """
        Add all elements from another paragraph to the end of this paragraph
        :param paragraph: The paragraph to add.
        :return: None
        """
        self._elements_list.extend(paragraph.get_elements())

    def get_elements(self) -> List:
        """
        Returns the list of elements of this paragraph.
        :return: the list of elements of this paragraph.
        """
        return self._elements_list

    def get_links(self) -> List[Link]:
        """
        Returns a list of Links inside this paragraph.
        :return: Returns a list of Links inside this paragraph.
        """
        link_list = []
        for element in self._elements_list:
            if isinstance(element, Link):
                link_list.append(element)
        return link_list

    def clear(self) -> None:
        """
        Clear all elements from this paragraph.
        :return: None
        """
        self._elements_list.clear()

    def __str__(self) -> str:
        return 'Paragraph: ' + str(self._elements_list)
