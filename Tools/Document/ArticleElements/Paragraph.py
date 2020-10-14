from typing import List


class Paragraph:
    """
    This class represents one paragraph in a article. A paragraph consists of a list of instances of text, break and
    link.
    """
    def __init__(self):
        """
        Constructor for paragraph.
        """
        self.elements_list = []

    def add_element(self, text_element) -> None:
        """
        Add an element to this paragraph. This can be Text or Link.
        :param text_element: The element to add.
        :return: None
        """
        self.elements_list.append(text_element)

    def get_elements(self) -> List:
        """
        Returns the list of elements of this paragraph.
        :return: the list of elements of this paragraph.
        """
        return self.elements_list

    def clear(self) -> None:
        """
        Clear all elements from this paragraph.
        :return: None
        """
        self.elements_list.clear()
